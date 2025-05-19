import streamlit as st
import google.generativeai as genai

def workflow_suggestion(mapping):
    st.subheader("B4. AI suggest workflow ETL")
    etl_tool = st.selectbox("Chọn tool ETL", ["Power Query", "Pentaho DI", "Airflow", "Python Pandas"])
    gemini_api_key = st.sidebar.text_input("Gemini API Key:", type="password")
    if st.button("AI suggest workflow ETL"):
        prompt = (
            f"Mapping đã chốt: {mapping}\n"
            f"Tool ETL: {etl_tool}\n"
            "Liệt kê từng bước transform ETL phù hợp tool."
        )
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        st.info(response.text)
        if st.button("OK, chốt workflow"):
            return response.text
    return None
