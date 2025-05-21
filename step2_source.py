import streamlit as st
from excel_loader import upload_and_extract_excel
from gemini_agent import query_gemini

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
        st.markdown("**Preview bảng nguồn (100 dòng đầu):**")
        st.dataframe(st.session_state['source_data'].head(100))

    # 4. Giao tiếp AI
    if st.session_state.get('gemini_api_key') and st.button("Gửi Gemini phân tích nguồn"):
        prompt = (
            f"{st.session_state['source_prompt_text']}\n"
            f"Dưới đây là toàn bộ dữ liệu file nguồn:\n"
            f"{st.session_state['source_data'].to_dict(orient='records')}"
        )
        response, err = query_gemini(prompt, st.session_state['gemini_api_key'])
        if err:
            st.error(err)
        else:
            st.session_state['source_response'] = response
            st.session_state['source_context'] = response

    # 5. Show response/context luôn giữ lại khi back/next
    if st.session_state['source_response']:
        st.markdown("**Response cuối của AI-agent:**")
        st.info(st.session_state['source_response'])
        st.markdown("**Context cuối dùng cho step sau:**")
        st.code(st.session_state['source_context'])
