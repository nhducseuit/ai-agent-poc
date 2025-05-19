import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def load_sheets():
    st.sidebar.header("B1. Kết nối & nhập dữ liệu")
    creds_file = st.sidebar.file_uploader("Tải credentials.json", type="json")
    src_sheet_id = st.sidebar.text_input("Sheet ID nguồn:")
    tgt_sheet_id = st.sidebar.text_input("Sheet ID đích:")
    reload_btn = st.sidebar.button("Load dữ liệu")

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    src_df, tgt_df = None, None

    if creds_file and src_sheet_id and tgt_sheet_id and reload_btn:
        try:
            creds_file.seek(0)
            creds_dict = eval(creds_file.read().decode())
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            gc = gspread.authorize(creds)

            # --- Đọc toàn bộ sheet nguồn, cho chọn dòng header ---
            src_all = gc.open_by_key(src_sheet_id).sheet1.get_all_values()
            st.write("Xem preview dữ liệu nguồn (5-20 dòng đầu):")
            st.write(pd.DataFrame(src_all[:20]))
            header_row = st.number_input("Chọn dòng header (tính từ 1)", min_value=1, max_value=len(src_all), value=1)
            header = src_all[header_row-1]
            data_rows = src_all[header_row:]
            # Chuẩn hóa chiều dài dòng cho vừa header
            data_fixed = [row + [None]*(len(header)-len(row)) if len(row)<len(header) else row for row in data_rows]
            src_df = pd.DataFrame(data_fixed, columns=header)
            st.write("**Nguồn:**", src_df.head(5))

            # Sheet đích: có thể cho phép chọn header tương tự, hoặc vẫn dùng get_all_records nếu chắc chắn bảng chuẩn
            tgt_all = gc.open_by_key(tgt_sheet_id).sheet1.get_all_values()
            st.write("Preview dữ liệu đích (5-20 dòng đầu):")
            st.write(pd.DataFrame(tgt_all[:20]))
            tgt_header_row = st.number_input("Dòng header của sheet đích (tính từ 1)", min_value=1, max_value=len(tgt_all), value=1, key="tgt_header")
            tgt_header = tgt_all[tgt_header_row-1]
            tgt_data_rows = tgt_all[tgt_header_row:]
            tgt_data_fixed = [row + [None]*(len(tgt_header)-len(row)) if len(row)<len(tgt_header) else row for row in tgt_data_rows]
            tgt_df = pd.DataFrame(tgt_data_fixed, columns=tgt_header)
            st.write("**Đích:**", tgt_df.head(3))

            st.success("Đã tải dữ liệu thành công!")
        except Exception as e:
            st.error(f"Lỗi đọc sheet: {e}")
    return src_df, tgt_df
