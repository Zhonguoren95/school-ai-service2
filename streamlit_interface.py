import streamlit as st
import pandas as pd
from core import process_documents

st.set_page_config(page_title="AI-сервис подбора оборудования", layout="wide")

st.title("🛠️ AI-сервис подбора оборудования")
st.markdown("Загрузите техническое задание, прайсы и (опционально) файл со скидками — система всё сделает сама.")

uploaded_spec = st.file_uploader("📄 Техническое задание (PDF)", type=["pdf"])
uploaded_prices = st.file_uploader("📊 Прайсы поставщиков (XLSX)", type=["xlsx"], accept_multiple_files=True)
uploaded_discounts = st.file_uploader("💸 Скидки от поставщиков (XLSX, по желанию)", type=["xlsx"])

if st.button("🚀 Запустить подбор"):
    if uploaded_spec and uploaded_prices:
        st.write("Файлы загружены, запуск обработки...")
        with st.spinner("⚙ Обработка данных..."):
            # временно отключаем try...except для отладки
            ts_text, result_df, result_file = process_documents(uploaded_spec, uploaded_prices, uploaded_discounts)

            st.success("✅ Подбор завершён!")

            st.subheader("🧾 Распознанный текст из ТЗ")
            st.text_area("Текст ТЗ (первые 1000 символов)", ts_text[:1000], height=200)

            st.subheader("📊 Результаты подбора")
            if not result_df.empty:
                st.dataframe(result_df, use_container_width=True)

                st.download_button(
                    label="📥 Скачать Excel",
                    data=result_file,
                    file_name="Результат_подбора.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠ Результат пуст. Возможно, не удалось найти совпадения.")
    else:
        st.warning("⚠ Необходимо загрузить ТЗ и хотя бы один прайс-лист.")
