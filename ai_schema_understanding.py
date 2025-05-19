import streamlit as st
import google.generativeai as genai

def ai_schema_understanding(src_df, tgt_df):
    st.subheader("B2. AI hiểu schema & xác nhận bài toán")
    gemini_api_key = st.sidebar.text_input("Gemini API Key:", type="password")
    if st.button("AI trình bày lại hiểu biết schema"):
        prompt = (
            f"Dữ liệu nguồn (mẫu): {src_df.head(5).to_dict('records')}\n"
            f"Schema đích: {list(tgt_df.columns)}\n"
            "Trình bày lại cấu trúc, các trường, datatype, nếu có trường nào không map được thì nêu rõ."
        )
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        st.info(response.text)
        if st.button("OK, xác nhận hiểu đúng"):
            return True
    return False
