# ✅ Новый рабочий код без pytesseract (OCR временно отключён)
# Используется pdfplumber для извлечения текста из PDF

import streamlit as st
import pandas as pd
import pdfplumber
import re
from openpyxl import load_workbook
from io import BytesIO

# --- Функции ---
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def parse_requirements(text):
    lines = text.split("\n")
    rows = []
    for line in lines:
        if any(char.isdigit() for char in line):
            parts = re.split(r"\s{2,}|\t", line.strip())
            if len(parts) >= 2:
                name = parts[0]
                quantity = re.search(r"\d+", parts[1])
                quantity = quantity.group() if quantity else ""
                rows.append({"Наименование из ТЗ": name, "Кол-во": quantity})
    return pd.DataFrame(rows)

def load_price_list(files):
    all_items = []
    for file in files:
        df = pd.read_excel(file, header=None)
        for index, row in df.iterrows():
            for col in row:
                if isinstance(col, str) and any(word in col.lower() for word in ["стол", "кресло", "лампа", "шкаф", "банкетка", "барьер"]):
                    item = {
                        "Артикул": row[0] if len(row) > 0 else "",
                        "Наименование": col,
                        "Цена": next((v for v in row if isinstance(v, (int, float))), "")
                    }
                    all_items.append(item)
                    break
    return pd.DataFrame(all_items)

def process_documents(spec_file, prices_files):
    text = extract_text_from_pdf(spec_file)
    ts_df = parse_requirements(text)
    prices_df = load_price_list(prices_files)

    results = []
    for _, row in ts_df.iterrows():
        name = row["Наименование из ТЗ"]
        qty = row["Кол-во"]
        match = prices_df[prices_df["Наименование"].str.contains(name.split()[0], case=False, na=False)]
        match = match.head(3)
        item = {
            "Наименование из ТЗ": name,
            "Кол-во": qty
        }
        for i, (_, mrow) in enumerate(match.iterrows(), start=1):
            item[f"Поставщик {i}"] = "Прайс"
            item[f"Цена {i}"] = mrow["Цена"]
        results.append(item)

    result_df = pd.DataFrame(results)

    # Загрузка шаблона Excel и заполнение
    wb = load_workbook("Форма для результата.xlsx")
    ws = wb.active
    start_row = 10
    for i, row in result_df.iterrows():
        ws.cell(row=start_row + i, column=1, value=i + 1)
        ws.cell(row=start_row + i, column=2, value=row["Наименование из ТЗ"])
        ws.cell(row=start_row + i, column=3, value=row["Кол-во"])
        ws.cell(row=start_row + i, column=4, value=row.get("Поставщик 1"))
        ws.cell(row=start_row + i, column=5, value=row.get("Цена 1"))

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return text[:1000], result_df, output.read()

# --- Интерфейс ---
st.set_page_config(page_title="AI-сервис подбора оборудования", layout="wide")
st.title("🤖 AI-сервис подбора оборудования")

uploaded_spec = st.file_uploader("📄 Техническое задание (PDF)", type="pdf")
uploaded_prices = st.file_uploader("📊 Прайсы поставщиков (XLSX)", type="xlsx", accept_multiple_files=True)

if st.button("🚀 Запустить подбор"):
    if uploaded_spec and uploaded_prices:
        with st.spinner("🔄 Обработка данных..."):
            ts_text, result_df, output_file = process_documents(uploaded_spec, uploaded_prices)
        st.success("✅ Подбор завершён")
        st.subheader("📑 Распознанный текст из ТЗ")
        st.text_area("Текст ТЗ (первые 1000 символов)", ts_text, height=200)

        st.subheader("📋 Результаты подбора")
        st.dataframe(result_df, use_container_width=True)

        st.download_button(
            label="💾 Скачать Excel",
            data=output_file,
            file_name="Результат_подбора.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("❗ Загрузите оба типа файлов: ТЗ и прайсы")
