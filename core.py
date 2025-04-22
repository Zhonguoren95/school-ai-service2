import pandas as pd
import pdfplumber
import re
from openpyxl import load_workbook
from io import BytesIO

import streamlit as st
from pdf2image import convert_from_bytes

def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"Ошибка при извлечении текста из PDF: {e}")
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
    df = pd.DataFrame(rows)
    st.write(f"Обнаружено позиций в ТЗ: {len(df)}")
    return df

def load_price_list(files):
    all_items = []
    for file in files:
        df = pd.read_excel(file, header=None)
        for index, row in df.iterrows():
            for col in row:
                if isinstance(col, str) and any(keyword in col.lower() for keyword in ["стол", "кресло", "лампа", "шкаф", "банкетка", "барьер"]):
                    item = {
                        "Артикул": row[0] if len(row) > 1 else "",
                        "Наименование": col,
                        "Цена": next((v for v in row if isinstance(v, (int, float))), "")
                    }
                    all_items.append(item)
                    break
    return pd.DataFrame(all_items)

def load_discounts(file):
    try:
        df = pd.read_excel(file)
        discounts = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        st.write(f"Загружено скидок: {len(discounts)}")
        return discounts
    except Exception as e:
        st.error(f"Ошибка при загрузке скидок: {e}")
        return {}

def process_documents(spec_file, prices_files, discounts_file=None):
    text = extract_text_from_pdf(spec_file)
    st.text_area("Извлечённый текст ТЗ (первые 1000 символов)", text[:1000])

    requirements_df = parse_requirements(text)
    if requirements_df.empty:
        st.warning("Не удалось распознать ни одной позиции в ТЗ. Проверьте файл.")
        return text, pd.DataFrame(), BytesIO()

    prices_df = load_price_list(prices_files)
    discounts = load_discounts(discounts_file) if discounts_file else {}

    results = []
    for _, req_row in requirements_df.iterrows():
        name = req_row["Наименование из ТЗ"]
        qty = req_row["Кол-во"]

        matches = prices_df[prices_df["Наименование"].str.contains(name.split()[0], case=False, na=False)].sort_values("Цена")[:3]

        item = {
            "Наименование из ТЗ": name,
            "Кол-во": qty,
        }

        for i, (_, match_row) in enumerate(matches.iterrows()):
            price = match_row.get("Цена")
            supplier = match_row.get("Поставщик", f"Поставщик {i+1}")
            discount = discounts.get(supplier, 0)
            final_price = round(price * (1 - discount / 100), 2) if price else ""

            item[f"Поставщик {i+1}"] = supplier
            item[f"Цена {i+1}"] = price
            item[f"Скидка {i+1}"] = f"{discount}%"
            item[f"Итог {i+1}"] = final_price

        results.append(item)

    result_df = pd.DataFrame(results)

    # Формируем Excel
    template = "Форма для результата.xlsx"
    wb = load_workbook(template)
    ws = wb.active

    start_row = 10
    for i, row in result_df.iterrows():
        ws.cell(row=start_row + i, column=1, value=i + 1)
        ws.cell(row=start_row + i, column=2, value=row["Наименование из ТЗ"])
        ws.cell(row=start_row + i, column=3, value=row["Кол-во"])
        ws.cell(row=start_row + i, column=4, value=row.get("Поставщик 1"))
        ws.cell(row=start_row + i, column=5, value=row.get("Цена 1"))
        ws.cell(row=start_row + i, column=6, value=row.get("Скидка 1"))
        ws.cell(row=start_row + i, column=7, value=row.get("Итог 1"))

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return text, result_df, output.read()
