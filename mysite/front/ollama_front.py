import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/ollama/ollama/"

st.set_page_config(page_title="Ollama Chat", layout="wide")

with st.sidebar:
    st.header("Настройки модели")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.50, 0.01)
    top_p = st.slider("Top P", 0.0, 1.0, 0.90, 0.01)
    top_k = st.slider("Top K", 0, 100, 2, 1)
    seed = st.number_input("Seed", value=44, step=1)

st.title("Введите текст")

user_text = st.text_area(
    "",
    placeholder="Вставьте сюда текст...",
    height=200,
    label_visibility="collapsed",
)

run_clicked = st.button("Запустить", use_container_width=True)

if run_clicked:
    if not user_text.strip():
        st.warning("Введите текст перед запуском.")
    else:
        payload = {
            "prompt": user_text,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "seed": int(seed),
        }

        with st.spinner("Ждём ответ от модели..."):
            try:
                resp = requests.post(API_URL, json=payload, timeout=300)
                resp.raise_for_status()
                st.session_state["result"] = resp.json()
            except requests.exceptions.RequestException as e:
                st.session_state["result"] = None
                st.error(f"Ошибка запроса к API: {e}")

result = st.session_state.get("result")

if result:
    st.subheader("Результат")
    st.markdown(result["answer"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Входные токены", result["input_tokens"])
    col2.metric("Выходные токены", result["output_tokens"])
    col3.metric("Всего токенов", result["total_tokens"])
    col4.metric("Время", f'{result["time_seconds"]:.2f} сек.')

    st.caption(
        f'Модель: {result["model"]} · '
        f'Причина завершения: {result.get("done_reason") or "—"}'
    )