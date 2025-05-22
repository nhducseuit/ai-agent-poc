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
    if "target_context" not in st.session_state:
        st.session_state["target_context"] = ""
    if "target_response" not in st.session_state:
        st.session_state["target_response"] = ""
    if "target_data" not in st.session_state:
        st.session_state["target_data"] = None

    uploaded = st.file_uploader("Upload file Excel ĐÍCH (.xlsx)", type="xlsx", key="target_file_uploader")
    if uploaded:
        st.session_state['target_file'] = uploaded
        tgt_data = upload_and_extract_excel(uploaded)
        st.session_state['target_data'] = tgt_data
        st.markdown("**Preview bảng đích (100 dòng đầu):**")
        st.dataframe(tgt_data.head(100))

    # Prompt text giữ trạng thái đang gõ
    st.session_state['target_prompt_text'] = st.text_area(
        "Prompt gửi AI về file đích (hoặc dùng mẫu sẵn):",
        value=st.session_state['target_prompt_text'],
        key="target_prompt"
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
            f"{feedback}\n"
            f"Dưới đây là toàn bộ dữ liệu file đích:\n"
            f"{st.session_state['target_data'].to_dict(orient='records')}"
        )
        response, err = query_gemini(final_prompt, st.session_state['gemini_api_key'])
        if err:
            st.error(err)
        else:
            st.session_state['target_response'] = response
            # Nếu bạn không tự trích lọc riêng, thì lấy luôn response làm context bước tiếp
            st.session_state['target_context'] = response
            append_context(1, "user", final_prompt)
            append_context(1, "assistant", response)

    # ==== 2 cột song song để so sánh context và response AI ====
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Context trích lọc được cho lần gửi prompt sau")
        st.session_state['target_context'] = st.text_area(
            "Bạn có thể chỉnh lại context này trước khi dùng cho bước sau:",
            value=st.session_state['target_context'],
            key="target_context_edit",
            height=250
        )
    with col2:
        st.markdown("#### Response cuối của AI-agent")
        if st.session_state['target_response']:
            st.info(st.session_state['target_response'])

