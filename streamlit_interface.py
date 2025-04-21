import streamlit as st
from core import process_documents

st.set_page_config(page_title="AI-сервис подбора оборудования", layout="wide")

st.title("🤖 AI-сервис подбора оборудования")
st.markdown("Загрузите техническое задание, прайс-листы и (по желанию) файл со скидками — система всё сделает сама.")

# Загрузка файлов
st.header("📄 Техническое задание")
tz_file = st.file_uploader("Загрузите файл с ТЗ (PDF, DOCX)", type=["pdf", "docx"], key="tz")

st.header("📊 Прайсы поставщиков")
price_files = st.file_uploader("Загрузите один или несколько прайсов (Excel)", type=["xlsx"], accept_multiple_files=True, key="prices")

st.header("💸 Скидки от поставщиков (по желанию)")
discount_file = st.file_uploader("Файл со скидками (Excel: Поставщик | Скидка в %)", type=["xlsx"], key="discount")

# Кнопка запуска
if st.button("🚀 Запустить подбор"):
    if tz_file and price_files:
        with st.spinner("Обработка данных..."):
            try:
                final_df, recognized_text = process_documents(tz_file, price_files, discount_file)

                st.success("Файлы обработаны успешно!")

                st.subheader("🧾 Распознанный текст из ТЗ")
                st.text(recognized_text[:1000])  # показать первые 1000 символов текста

                st.subheader("📋 Объединённый прайс-лист")
                st.dataframe(final_df, use_container_width=True)

                # Скачивание результата
                st.download_button(
                    label="💾 Скачать результат (Excel)",
                    data=final_df.to_excel(index=False),
                    file_name="Результат подбора.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Произошла ошибка при обработке: {e}")
    else:
        st.warning("Пожалуйста, загрузите как минимум файл с ТЗ и один прайс.")
