import streamlit as st
import google.generativeai as genai

def mapping_step(src_df, tgt_df):
    st.subheader("B3. Mapping")
    mapping_mode = st.radio("Chọn kiểu mapping", ["AI suggest", "Nhập text"])
    gemini_api_key = st.sidebar.text_input("Gemini API Key:", type="password")
    mapping = ""
    if mapping_mode == "AI suggest":
        if st.button("AI mapping"):
            prompt = (
                f"Dữ liệu nguồn (sample): {src_df.head(5).to_dict('records')}\n"
                f"Schema đích: {list(tgt_df.columns)}\n"
                "Mapping từng trường đích với trường nguồn, ghi rõ nếu cần transform."
            )
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            mapping = response.text
            st.info(mapping)
    else:
        mapping = st.text_area("Nhập mapping dạng text:", height=100)
    if mapping and st.button("OK, chốt mapping"):
        return mapping
    return None
