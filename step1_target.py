import streamlit as st
from excel_loader import upload_and_extract_excel
from gemini_agent import query_gemini

def step1_target():
    st.header("Step 1: Định nghĩa ngoại cảnh bảng tính ĐÍCH (Target Sheet)")

    # Lưu trạng thái các biến UI (file, prompt, data, response)
    if 'target_file' not in st.session_state:
        st.session_state['target_file'] = None
    if 'target_prompt_text' not in st.session_state:
        st.session_state['target_prompt_text'] = "Hãy phân tích file Excel đích, xác định rõ vùng dữ liệu, dòng header, liệt kê schema, các trường và kiểu dữ liệu. Ghi nhớ schema/context để sử dụng cho các bước tiếp theo."
    if 'target_data' not in st.session_state:
        st.session_state['target_data'] = None
    if 'target_response' not in st.session_state:
        st.session_state['target_response'] = ""
    if 'target_context' not in st.session_state:
        st.session_state['target_context'] = ""

    # 1. File uploader - giữ lại file trong session_state
    uploaded = st.file_uploader("Upload file Excel ĐÍCH (.xlsx)", type="xlsx", key="target_file_uploader")
    if uploaded:
        st.session_state['target_file'] = uploaded
        tgt_data = upload_and_extract_excel(uploaded)
        st.session_state['target_data'] = tgt_data

    # 2. Prompt text - giữ text đang gõ trong session_state
    st.session_state['target_prompt_text'] = st.text_area(
        "Prompt gửi AI về file đích (hoặc dùng mẫu sẵn bên dưới):",
        value=st.session_state['target_prompt_text'],
        key="target_prompt"
    )

    # 3. Preview - nếu đã có file và dataframe thì show lại preview
    if st.session_state['target_data'] is not None:
        st.markdown("**Preview bảng đích (100 dòng đầu):**")
        st.dataframe(st.session_state['target_data'].head(100))

    # 4. Giao tiếp AI
    if st.session_state.get('gemini_api_key') and st.button("Gửi Gemini phân tích đích"):
        prompt = (
            f"{st.session_state['target_prompt_text']}\n"
            f"Dưới đây là toàn bộ dữ liệu file đích:\n"
            f"{st.session_state['target_data'].to_dict(orient='records')}"
        )
        response, err = query_gemini(prompt, st.session_state['gemini_api_key'])
        if err:
            st.error(err)
        else:
            st.session_state['target_response'] = response
            st.session_state['target_context'] = response

    # 5. Show response/context luôn giữ lại khi back/next
    if st.session_state['target_response']:
        st.markdown("**Response cuối của AI-agent:**")
        st.info(st.session_state['target_response'])
        st.markdown("**Context cuối dùng cho step sau:**")
        st.code(st.session_state['target_context'])
