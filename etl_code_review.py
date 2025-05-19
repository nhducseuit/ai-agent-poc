import streamlit as st
import google.generativeai as genai

def etl_code_review(etl_code):
    st.subheader("B6. AI code reviewer")
    gemini_api_key = st.sidebar.text_input("Gemini API Key:", type="password")
    if st.button("AI review code ETL"):
        prompt = (
            f"Review code ETL sau:\n{etl_code}\n"
            "Nhận xét về logic, bug, tối ưu, cảnh báo edge case, bảo mật."
        )
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        st.info(response.text)
        if st.button("OK, kết thúc review"):
            return True
    return False
