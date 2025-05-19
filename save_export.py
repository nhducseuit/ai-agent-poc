import streamlit as st

def save_etl_code(etl_code):
    st.subheader("B7. Xuất/lưu code ETL")
    st.download_button("Tải code ETL", etl_code, file_name="etl_code.txt")
    st.success("Hoàn thành quy trình ETL với AI agent!")
