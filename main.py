import streamlit as st
from step1_target import step1_target
from step2_source import step2_source
from step3_mapping import step3_mapping
import os
from dotenv import load_dotenv

load_dotenv()

def get_gemini_api_key():
    # Ưu tiên lấy từ biến môi trường, nếu không có thì lấy từ session_state
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key
    # Fallback: lấy key user nhập ở UI nếu cần
    return st.session_state.get('gemini_api_key')

st.set_page_config(page_title="ETL Agent Wizard", layout="centered")
st.title("🚦 ETL AI-Agent Wizard (Human-in-the-loop)")

if 'step' not in st.session_state: st.session_state['step'] = 1

def reset_flow():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state['step'] = 1

col_btns = st.columns([1,1,1,1])
with col_btns[0]:
    if st.button("⏹️ Cancel Flow"):
        reset_flow()
        st.rerun()
with col_btns[2]:
    if st.session_state['step'] > 1 and st.button("⬅️ Back"):
        st.session_state['step'] -= 1
        st.rerun()
with col_btns[3]:
    if st.session_state['step'] < 3 and st.button("Next ➡️"):
        st.session_state['step'] += 1
        st.rerun()

gemini_api_key = get_gemini_api_key()
st.session_state['gemini_api_key'] = gemini_api_key

# Step router
if st.session_state['step'] == 1:
    step1_target()
elif st.session_state['step'] == 2:
    step2_source()
elif st.session_state['step'] == 3:
    step3_mapping()
