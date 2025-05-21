import streamlit as st
from gemini_agent import query_gemini

def step3_mapping():
    st.header("Step 3: Xây dựng context mapping NGUỒN <-> ĐÍCH")
    st.markdown("#### Context bảng tính ĐÍCH:")
    st.code(st.session_state.get('target_context', ''))
    st.markdown("#### Context bảng tính NGUỒN:")
    st.code(st.session_state.get('source_context', ''))

    user_prompt = st.text_area(
        "Prompt gửi AI để sinh mapping (hoặc dùng mẫu):",
        value=(
            "Dựa vào context/schema của file nguồn và đích bên trên, hãy đề xuất bảng mapping trường từ nguồn sang đích, "
            "ghi rõ từng cặp mapping (source_field, target_field, transform nếu có, note). Trả về dưới dạng bảng để tôi dễ kiểm tra. "
            "Nếu cần, bạn có thể đề xuất chỉnh sửa lại context."
        ),
        key="mapping_prompt"
    )
    if st.button("Gửi Gemini tạo mapping"):
        if not st.session_state.get('gemini_api_key'):
            st.warning("Bạn cần nhập Gemini API Key!")
        else:
            prompt = (
                f"{user_prompt}\n\n"
                "Context file đích:\n" + st.session_state.get('target_context', '') +
                "\n\nContext file nguồn:\n" + st.session_state.get('source_context', '')
            )
            response, err = query_gemini(prompt, st.session_state['gemini_api_key'])
            if err:
                st.error(err)
            else:
                st.session_state['mapping_response'] = response
                st.session_state['mapping_context'] = response

    if st.session_state.get('mapping_response'):
        st.markdown("**Mapping cuối do AI-agent trả về:**")
        st.info(st.session_state['mapping_response'])
        st.markdown("**Context mapping cho các bước ETL tiếp:**")
        st.code(st.session_state['mapping_context'])
