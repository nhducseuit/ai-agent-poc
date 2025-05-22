import streamlit as st
from excel_loader import upload_and_extract_excel
from gemini_agent import query_gemini
from context_manager import append_context, get_history_context_str

def step2_source():
    st.header("Step 2: Định nghĩa ngoại cảnh bảng tính NGUỒN (Source Sheet)")

    # Giữ trạng thái các biến UI (file, prompt, data, response)
    if 'source_file' not in st.session_state:
        st.session_state['source_file'] = None
    if 'source_prompt_text' not in st.session_state:
        st.session_state['source_prompt_text'] = "Hãy phân tích file Excel nguồn, xác định vùng bảng dữ liệu, dòng header, liệt kê schema, các trường và kiểu dữ liệu. Ghi nhớ context/schema để dùng cho các bước tiếp theo."
    if 'source_data' not in st.session_state:
        st.session_state['source_data'] = None
    if 'source_response' not in st.session_state:
        st.session_state['source_response'] = ""
    if 'source_context' not in st.session_state:
        st.session_state['source_context'] = ""
    if 'source_range_start' not in st.session_state:
        st.session_state['source_range_start'] = 0
    if 'source_range_end' not in st.session_state:
        st.session_state['source_range_end'] = 20

    # 1. File uploader - lưu lại file đã upload trong session_state
    uploaded = st.file_uploader("Upload file Excel NGUỒN (.xlsx)", type="xlsx", key="source_file_uploader")
    if uploaded:
        st.session_state['source_file'] = uploaded
        src_data = upload_and_extract_excel(uploaded)
        st.session_state['source_data'] = src_data

    # 2. Prompt text - giữ text đang gõ trong session_state
    st.session_state['source_prompt_text'] = st.text_area(
        "Prompt gửi AI về file nguồn (hoặc dùng mẫu sẵn):",
        value=st.session_state['source_prompt_text'],
        key="source_prompt"
    )

    # 3. Preview - nếu đã có file và dataframe thì show lại preview
    if st.session_state['source_data'] is not None:
        src_data = st.session_state['source_data']
        st.markdown("**Preview bảng nguồn (100 dòng đầu):**")
        st.dataframe(src_data.head(100))

        total_rows = len(src_data)
        st.markdown(f"File này có tổng {total_rows} dòng dữ liệu.")

        # Range picker UI (chỉ đọc, không set lại session_state)
        start_row = st.number_input(
            "Dòng bắt đầu gửi (từ 0)",
            min_value=0,
            max_value=max(total_rows-1, 0),
            value=st.session_state.get('source_range_start', 0),
            step=1,
            key="source_range_start"
        )
        end_row = st.number_input(
            "Dòng kết thúc gửi (exclusive)",
            min_value=start_row+1,
            max_value=total_rows,
            value=min(start_row+20, total_rows),
            step=1,
            key="source_range_end"
        )

        portion = src_data.iloc[start_row:end_row]

        st.markdown(f"**Sẽ gửi {len(portion)} dòng (từ dòng {start_row} đến {end_row-1})**")
        st.dataframe(portion)

        # 4. Giao tiếp AI (luôn truyền context schema đích của step trước)
        if st.session_state.get('gemini_api_key') and st.button("Gửi Gemini phân tích nguồn"):
            context_before = get_history_context_str(upto_step=1)
            prompt = (
                f"{context_before}\n"
                f"\n[Step 2][user]:\n{st.session_state['source_prompt_text']}\n"
                f"Dưới đây là {len(portion)} dòng (range {st.session_state['source_range_start']}–{st.session_state['source_range_end']-1}) của file nguồn:\n"
                f"{portion.to_dict(orient='records')}"
            )
            response, err = query_gemini(prompt, st.session_state['gemini_api_key'])
            if err:
                st.error(err)
            else:
                st.session_state['source_response'] = response
                st.session_state['source_context'] = response
                append_context(2, "user", prompt)
                append_context(2, "assistant", response)

    # 5. Show response/context luôn giữ lại khi back/next
    if st.session_state['source_response']:
        st.markdown("**Response cuối của AI-agent:**")
        st.info(st.session_state['source_response'])
        st.markdown("**Context cuối dùng cho step sau:**")
        st.code(st.session_state['source_context'])
