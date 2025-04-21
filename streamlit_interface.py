import streamlit as st
import pandas as pd
import traceback

st.set_page_config(page_title="AI-сервис подбора оборудования")

st.markdown("## 🧑‍💻 AI-сервис подбора оборудования")
st.markdown("""
Загрузите техническое задание и прайс-листы — система всё сделает сама.
""")

try:
    # --- ТЗ ---
    st.subheader(":bookmark_tabs: Техническое задание")
    tz_file = st.file_uploader("Загрузите файл с ТЗ (PDF, DOCX)", type=["pdf", "docx"])

    # --- Прайсы ---
    st.subheader(":bar_chart: Прайсы поставщиков")
    price_files = st.file_uploader("Загрузите 1 или несколько прайсов (Excel)", type=["xlsx"], accept_multiple_files=True)

    # --- Скидки ---
    st.subheader(":money_with_wings: Скидки от поставщиков (по желанию)")
    discount_file = st.file_uploader("Файл со скидками (Excel)", type=["xlsx"])

    # --- Кнопка запуска ---
    if st.button("Запустить подбор"):
        st.success("Файлы получены! Идёт обработка...")

        if tz_file is not None:
            st.write("Файл ТЗ:", tz_file.name)
        else:
            st.warning("Файл ТЗ не загружен")

        if price_files:
            st.write(f"Загружено прайсов: {len(price_files)}")
        else:
            st.warning("Нет прайсов для анализа")

        if discount_file:
            st.write("Загружен файл со скидками:", discount_file.name)

        # ВРЕМЕННО: заглушка до полной логики обработки
        st.info("Обработка временно отключена. Интерфейс работает корректно.")

except Exception as e:
    st.error("Произошла ошибка:")
    st.code(traceback.format_exc())

