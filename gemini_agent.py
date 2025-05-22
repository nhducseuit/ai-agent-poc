import google.generativeai as genai

def query_gemini(prompt, api_key):
    if not api_key or not prompt:
        return None, "Chưa nhập Gemini API Key hoặc prompt!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, f"Lỗi Gemini: {e}"
