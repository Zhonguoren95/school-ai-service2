import streamlit as st
import pandas as pd
from core import process_documents

st.set_page_config(page_title="AI-сервис подбора оборудования", layout="wide")

st.markdown("<h1 style='font-size: 36px;'>🤖 AI-сервис подбора оборудования</h1>", unsafe_allow_html=True)
st.write("Загрузите техническое задание, прайсы и файл со скидками — система всё сделает сама.")

uploaded_spec = st.file_uploader("📄 Техническое задание (PDF, DOCX)", type=["pdf", "docx"])
uploaded_prices = st.file_uploader("📊 Прайсы поставщиков (XLSX)", type=["xlsx"], accept_multiple_files=True)
uploaded_discounts = st.file_uploader("💸 Скидки от поставщиков (XLSX, необязательно)", type=["xlsx"])

if st.button("🚀 Запустить подбор"):
    if uploaded_spec and uploaded_prices:
        with st.spinner("Обработка..."):
            ts_text, df_result, result_file = process_documents(uploaded_spec, uploaded_prices, uploaded_discounts)

        st.success("Подбор завершён!")

        st.subheader("📜 Распознанный текст из ТЗ")
        st.text_area("ТЗ (первые 1000 символов)", ts_text[:1000])

        st.subheader("📋 Результаты подбора")
        st.dataframe(df_result)

        st.download_button(
            "📥 Скачать Excel",
            data=result_file,
            file_name="Результат_подбора.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Пожалуйста, загрузите ТЗ и хотя бы один прайс.")

