import streamlit as st
from data_input import load_sheets
from ai_schema_understanding import ai_schema_understanding
from mapping_step import mapping_step
from workflow_suggestion import workflow_suggestion
from etl_code_generation import etl_code_generation
from etl_code_review import etl_code_review
from save_export import save_etl_code

st.set_page_config(page_title="AI ETL Agent Pro", layout="wide")
st.title("AI ETL Agent - Professional Flow (Module version)")

# Step 1: Đọc dữ liệu, schema
src_df, tgt_df = load_sheets()
if src_df is not None and tgt_df is not None:
    # Step 2: AI trình bày lại hiểu biết về schema/sample
    if ai_schema_understanding(src_df, tgt_df):
        # Step 3: Mapping step
        mapping = mapping_step(src_df, tgt_df)
        if mapping:
            # Step 4: Suggest workflow transform
            workflow = workflow_suggestion(mapping)
            if workflow:
                # Step 5: Sinh code ETL
                etl_code = etl_code_generation(mapping, workflow)
                if etl_code:
                    # Step 6: Review code ETL
                    if etl_code_review(etl_code):
                        # Step 7: Lưu/export code
                        save_etl_code(etl_code)
