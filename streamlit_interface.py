import streamlit as st
from core import process_documents

st.set_page_config(page_title="AI-сервис подбора оборудования", layout="wide")
st.title("🤖 AI-сервис подбора оборудования")
st.markdown("Загрузите техническое задание и прайс-листы — система всё сделает сама.")

uploaded_spec = st.file_uploader("\U0001F4C4 Техническое задание", type=["pdf", "docx"], help="Загрузите файл с ТЗ")
uploaded_prices = st.file_uploader("\U0001F4CA Прайсы поставщиков", type=["xlsx"], accept_multiple_files=True, help="Загрузите прайс-листы (можно несколько)")
uploaded_discounts = st.file_uploader("\U0001F4B8 Скидки от поставщиков (по желанию)", type=["xlsx"], help="Файл со скидками (опционально)")

if st.button("\u23F1 Запустить подбор"):
    if uploaded_spec and uploaded_prices:
        with st.spinner("\u2699\ufe0f Обработка файлов..."):
            try:
                result_df, extracted_text = process_documents(uploaded_spec, uploaded_prices, uploaded_discounts)
                st.success("Готово!")

                st.subheader("\U0001F4D6 Распознанный текст из ТЗ")
                st.code(extracted_text, language="text")

                st.subheader("\U0001F4CB Объединённый прайс-лист")
                st.dataframe(result_df, use_container_width=True)

                st.download_button(
                    label="\U0001F4E5 Скачать результат в Excel",
                    data=result_df.to_excel(index=False, engine="openpyxl"),
                    file_name="результат_podbor.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Произошла ошибка при обработке: {e}")
    else:
        st.warning("Пожалуйста, загрузите как минимум ТЗ и один прайс-лист.")
