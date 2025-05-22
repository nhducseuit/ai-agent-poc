import streamlit as st
from excel_loader import upload_and_extract_excel
from gemini_agent import query_gemini
from context_manager import append_context

def step1_target():
    st.header("Step 1: Định nghĩa ngoại cảnh bảng tính ĐÍCH (Target Sheet)")
    
    # Khởi tạo session_state nếu chưa có
    if "target_file" not in st.session_state:
        st.session_state["target_file"] = None
    if "target_prompt_text" not in st.session_state:
        st.session_state["target_prompt_text"] = "Hãy phân tích file Excel đích, xác định rõ vùng dữ liệu, dòng header, liệt kê schema, các trường và kiểu dữ liệu. Ghi nhớ schema/context để sử dụng cho các bước tiếp theo."
    if "target_feedback" not in st.session_state:
        st.session_state["target_feedback"] = ""
    if "last_ai_response_text" not in st.session_state:
        st.session_state["last_ai_response_text"] = ""
    if "target_response" not in st.session_state:
        st.session_state["target_response"] = ""
    if "target_data" not in st.session_state:
        st.session_state["target_data"] = None
    if "target_data_sent" not in st.session_state:
        st.session_state["target_data_sent"] = None

    uploaded = st.file_uploader("Upload file Excel ĐÍCH (.xlsx)", type="xlsx", key="target_file_uploader")

    # ==== 2 cột song song để so sánh context và response AI ====
    col1, col2 = st.columns(2)
    with col1:
        if uploaded:
            st.session_state['target_file'] = uploaded
            tgt_data = upload_and_extract_excel(uploaded)
            st.session_state['target_data'] = tgt_data
            st.markdown("**Preview bảng đích (100 dòng đầu):**")
            st.dataframe(tgt_data.head())
            total_rows = len(tgt_data)
            st.markdown(f"File này có tổng {total_rows} dòng dữ liệu.")
            # Chọn range dòng gửi Gemini (có thể đổi thành start_row, end_row tuỳ ý)
            st.markdown(f"Chọn range dòng gửi Gemini:")
            start_row = st.number_input(
                "Dòng bắt đầu gửi (từ 0)", min_value=0, max_value=max(total_rows-1,0), value=0, step=1, key="target_range_start"
            )
            end_row = st.number_input(
                "Dòng kết thúc gửi (exclusive)", min_value=start_row+1, max_value=total_rows, value=min(start_row+20, total_rows), step=1, key="target_range_end"
            )
            st.session_state['target_data_sent'] = tgt_data.iloc[start_row:end_row]
        
        st.markdown("#### Context trích lọc được gửi cho prompt")
        st.text_area(
            "Context kế thừa từ prompt trước đó:",
            value=st.session_state['last_ai_response_text'],
            key="last_ai_response_text_edit",
            height=250
        )
        
        # Developer bổ sung feedback trước khi gửi lại Gemini
        feedback = st.text_area(
            "Bổ sung feedback, yêu cầu, chú thích thêm gửi cho Gemini (nếu cần):",
            value=st.session_state['target_feedback'],
            key="target_feedback"
        )
        # Nút gửi Gemini
        if st.session_state.get('gemini_api_key') and st.button("Gửi Gemini phân tích đích"):
            final_prompt = (
                f"{st.session_state['target_prompt_text']}\n"
                f"Dưới đây là dữ liệu bảng đích đã xử lý và chỉ giữ lại cell value để giảm kích thước prompt:\n"
                f"{st.session_state['target_data_sent'].to_dict(orient='records')}"
                f"Dưới đây là phản hồi cuối cùng bạn gửi cho tôi:\n"
                f"{st.session_state['last_ai_response_text']}\n"
                f"Dưới đây là phản hồi của tôi đối với phản hồi của bạn:\n"
                f"{feedback}\n"
            )
            response, err = query_gemini(final_prompt, st.session_state['gemini_api_key'])
            if err:
                st.error(err)
            else:
                st.session_state['target_response'] = response
                # Nếu bạn không tự trích lọc riêng, thì lấy luôn response làm context bước tiếp
                st.session_state['last_ai_response_text'] = response
                append_context(1, "user", final_prompt)
                append_context(1, "assistant", response)
    with col2:
        st.markdown("#### Response cuối của AI-agent")
        if st.session_state['target_response']:
            st.info(st.session_state['target_response'])

