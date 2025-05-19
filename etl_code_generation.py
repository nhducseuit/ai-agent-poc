import streamlit as st
import google.generativeai as genai

def etl_code_generation(mapping, workflow):
    st.subheader("B5. AI sinh code ETL")
    etl_tool = st.selectbox("Chọn tool ETL", ["Power Query", "Pentaho DI", "Airflow", "Python Pandas"])
    gemini_api_key = st.sidebar.text_input("Gemini API Key:", type="password")
    if st.button("AI sinh code ETL"):
        prompt = (
            f"Mapping: {mapping}\n"
            f"Workflow: {workflow}\n"
            f"Tool ETL: {etl_tool}\n"
            "Sinh code hoàn chỉnh thực hiện ETL."
        )
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        st.code(response.text, language="python" if etl_tool=="Python Pandas" else None)
        if st.button("OK, chốt code"):
            return response.text
    return None
