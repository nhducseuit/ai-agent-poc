import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import google.generativeai as genai
import io

st.set_page_config(page_title="Gemini ETL - Raw Sheet Cleaner", layout="wide")
st.title("ETL AI: Làm sạch Google Sheet freestyle bằng Gemini")

st.sidebar.header("Thiết lập")
creds_file = st.sidebar.file_uploader("Tải credentials.json (service account)", type="json")
gemini_api_key = st.sidebar.text_input("Nhập Gemini API Key:", type="password")
sheet_id = st.sidebar.text_input("Google Sheet ID nguồn:")
reload_btn = st.sidebar.button("Load lại dữ liệu")

# --- Đọc Google Sheet, không cần bảng chuẩn ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "raw_values" not in st.session_state:
    st.session_state["raw_values"] = None

if creds_file and sheet_id and reload_btn:
    try:
        creds_file.seek(0)
        creds_dict = eval(creds_file.read().decode())
        if creds_dict.get("type") != "service_account":
            st.error("File credentials không đúng loại service account!")
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            gc = gspread.authorize(creds)
            sheet = gc.open_by_key(sheet_id).sheet1
            raw_values = sheet.get_all_values()
            st.session_state["raw_values"] = raw_values
            st.success(f"Đã tải {len(raw_values)} dòng dữ liệu raw từ Google Sheet!")
    except Exception as e:
        st.error(f"Lỗi khi tải sheet: {e}")

raw_values = st.session_state.get("raw_values")

# --- Hiển thị dữ liệu raw cho bạn kiểm tra ---
if raw_values is not None:
    st.subheader("Dữ liệu raw (mọi dòng, mọi cột):")
    max_show = st.number_input("Hiển thị bao nhiêu dòng đầu?", 5, min(30, len(raw_values)), value=min(15, len(raw_values)))
    st.write(pd.DataFrame(raw_values[:max_show]))

    # Cho phép chọn số dòng gửi tới AI (có thể gửi cả file nếu nhẹ)
    n_send = st.number_input("Số dòng gửi AI xử lý:", min_value=5, max_value=len(raw_values), value=min(20, len(raw_values)))
    raw_to_ai = raw_values[:n_send]

    # Nhập yêu cầu cho AI
    st.subheader("Nhập yêu cầu cho Gemini (có thể để trống):")
    user_inst = st.text_area(
        "Yêu cầu làm sạch, chuẩn hóa (ví dụ: bỏ dòng note, tìm dòng header, chuẩn hóa ngày tháng, tách họ tên...)", value="", height=80
    )

    # Prompt mẫu cho Gemini
    base_prompt = (
        "Dưới đây là dữ liệu raw từ Google Sheet (có thể gồm dòng trắng, tiêu đề phụ, ghi chú, header không chuẩn):\n"
        f"{raw_to_ai}\n"
        "Hãy xác định dòng nào là header thật sự và phần bảng chính, rồi sinh code Python pandas để:\n"
        "- Làm sạch dữ liệu: bỏ dòng thừa/trắng/note, xác định header đúng, điền None cho giá trị thiếu.\n"
        "- Nếu có thể, chuẩn hóa lại header (bỏ dấu, viết thường).\n"
        "- Tạo DataFrame pandas với dữ liệu sạch.\n"
        "- Giải thích logic làm sạch, xử lý.\n"
    )
    if user_inst.strip():
        base_prompt += "Yêu cầu bổ sung:\n" + user_inst.strip()

    # Nút gửi Gemini
    if st.button("Gửi Gemini AI, sinh code làm sạch & giải thích"):
        if not gemini_api_key:
            st.warning("Bạn chưa nhập Gemini API Key!")
        else:
            with st.spinner("Đang gửi tới Gemini..."):
                try:
                    genai.configure(api_key=gemini_api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(base_prompt)
                    st.markdown("### Kết quả từ Gemini:")
                    st.info(response.text)
                    # Trích xuất code từ kết quả trả về
                    import re
                    code_blocks = re.findall(r"```(?:python)?(.*?)```", response.text, re.DOTALL)
                    if code_blocks:
                        code_text = code_blocks[0].strip()
                        st.code(code_text, language="python")
                        # Nút chạy thử code trên dữ liệu thực tế
                        if st.checkbox("Thực thi code AI trên dữ liệu raw"):
                            try:
                                # Chuẩn bị biến all_values cho code
                                local_vars = {"all_values": raw_values.copy(), "pd": pd}
                                exec(code_text, {}, local_vars)
                                # Lấy DataFrame kết quả từ biến 'df' hoặc 'result'
                                transformed_df = None
                                if "df" in local_vars and isinstance(local_vars["df"], pd.DataFrame):
                                    transformed_df = local_vars["df"]
                                elif "result" in local_vars and isinstance(local_vars["result"], pd.DataFrame):
                                    transformed_df = local_vars["result"]
                                if transformed_df is not None:
                                    st.success("Kết quả DataFrame sau khi làm sạch:")
                                    st.dataframe(transformed_df)
                                    # Nút ghi lại vào Sheet mới (tùy chọn)
                                    if st.button("Ghi kết quả vào Sheet nguồn (replace all)?"):
                                        try:
                                            creds_file.seek(0)
                                            creds_dict = eval(creds_file.read().decode())
                                            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                                            gc = gspread.authorize(creds)
                                            sheet = gc.open_by_key(sheet_id).sheet1
                                            sheet.clear()
                                            sheet.update([transformed_df.columns.values.tolist()] + transformed_df.values.tolist())
                                            st.success("Đã ghi DataFrame sạch vào Sheet!")
                                        except Exception as e:
                                            st.error(f"Lỗi ghi sheet: {e}")
                                else:
                                    st.warning("Không tìm thấy DataFrame kết quả từ code AI!")
                            except Exception as ex:
                                st.error(f"Lỗi khi thực thi code AI: {ex}")
                    else:
                        st.warning("Không tìm thấy code Python trong kết quả trả về của Gemini.")
                except Exception as e:
                    st.error(f"Lỗi khi gửi Gemini: {e}")
else:
    st.info("Nhập credentials, Sheet ID và bấm 'Load lại dữ liệu' để bắt đầu.")
