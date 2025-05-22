import streamlit as st

# Mỗi step, context sẽ là 1 entry dạng {"role": "user"/"assistant", "content": "..."}
def append_context(step, role, content):
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    st.session_state['history'].append({
        "step": step,
        "role": role,
        "content": content
    })

def get_history_context_str(upto_step=None):
    # Ghép các prompt/response từ step đầu tới step hiện tại thành một chuỗi context lớn
    ctx = ""
    for entry in st.session_state.get('history', []):
        if upto_step is None or entry['step'] <= upto_step:
            ctx += f"\n[Step {entry['step']}][{entry['role']}]:\n{entry['content']}\n"
    return ctx.strip()

def reset_history():
    st.session_state['history'] = []
