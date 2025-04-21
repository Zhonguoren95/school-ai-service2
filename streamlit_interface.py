import streamlit as st
from core import process_documents

st.set_page_config(page_title="AI-сервис подбора оборудования", layout="wide")

st.markdown("<h1 style='font-size: 36px;'>🤖 AI-сервис подбора оборудования</h1>", unsafe_allow_html=True)
st.write("Загрузите техническое задание, прайс-листы и (опционально) файл со скидками — система всё сделает сама.")

uploaded_spec = st.file_uploader("📄 Техническое задание (PDF, DOCX)", type=["pdf", "docx"])
uploaded_prices = st.file_uploader("📊 Прайсы поставщиков (XLSX)", type=["xlsx"], accept_multiple_files=True)
uploaded_discounts = st.file_uploader("💸 Скидки от поставщиков (XLSX, необязательно)", type=["xlsx"])

if st.button("🚀 Запустить подбор"):
    if uploaded_spec and uploaded_prices:
        with st.spinner("Обработка..."):
            result_df, recognized_text = process_documents(uploaded_spec, uploaded_prices, uploaded_discounts)
        st.success("Готово!")

        st.subheader("📝 Распознанный текст из ТЗ")
        st.text_area("Текст ТЗ", recognized_text, height=200)

        st.subheader("📋 Объединённый прайс-лист")
        st.dataframe(result_df)

        st.download_button("📥 Скачать результат в Excel", data=result_df.to_excel(index=False), file_name="результат.xlsx")
    else:
        st.warning("Загрузите
