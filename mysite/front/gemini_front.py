import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/pdd/predict/"

st.set_page_config(page_title="Распознавание знаков ПДД", layout="wide")

with st.sidebar:
    st.header("Настройки модели")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.30, 0.01)
    top_p = st.slider("Top P", 0.0, 1.0, 0.90, 0.01)
    top_k = st.slider("Top K", 0, 100, 40, 1)
    seed = st.number_input("Seed", value=42, step=1)

st.title("Загрузите фото дорожного знака")

uploaded_file = st.file_uploader(
    "Загрузите фото знака",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed",
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="Загруженное фото", width=350)

run_clicked = st.button("Распознать", use_container_width=True)

if run_clicked:
    if uploaded_file is None:
        st.warning("Сначала загрузите фото.")
    else:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        params = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "seed": int(seed),
        }

        with st.spinner("Распознаём знак..."):
            try:
                resp = requests.post(API_URL, files=files, params=params, timeout=120)
                if resp.status_code != 200:
                    st.error(f"Ошибка {resp.status_code}: {resp.text}")
                    st.session_state["result"] = None
                else:
                    st.session_state["result"] = resp.json()
            except requests.exceptions.RequestException as e:
                st.session_state["result"] = None
                st.error(f"Ошибка запроса к API: {e}")

result = st.session_state.get("result")

if result:
    st.subheader("Результат")

    if result["is_sign"]:
        st.markdown(f"**Знак:** {result['name']}")
        st.markdown(f"**Категория:** {result['category']}")
        st.markdown(f"**Описание:** {result['description']}")
    else:
        st.warning(f"Знак не найден на фото. {result.get('comment') or ''}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Входные токены", result.get("input_tokens") or "—")
    col2.metric("Выходные токены", result.get("output_tokens") or "—")
    col3.metric("Всего токенов", result.get("total_tokens") or "—")
    col4.metric("Время", f'{result["time_seconds"]:.2f} сек.')

    st.caption(
        f'Модель: {result["model"]} · '
        f'Причина завершения: {result.get("done_reason") or "—"}'
    )