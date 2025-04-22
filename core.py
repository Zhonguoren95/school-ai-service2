import pandas as pd
import pdfplumber
import re
from openpyxl import load_workbook
from io import BytesIO

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
    df = pd.read_excel(file)
    return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

def process_documents(spec_file, prices_files, discounts_file=None):
    text = extract_text_from_pdf(spec_file)
    ts_text = text[:1000]  # первые 1000 символов
    spec_df = parse_requirements(text)
    prices_df = load_price_list(prices_files)
    discounts = load_discounts(discounts_file) if discounts_file else {}

    results = []
    for _, row in spec_df.iterrows():
        name = row["Наименование из ТЗ"]
        qty = row["Кол-во"]
        matches = prices_df[prices_df["Наименование"].str.contains(name.split()[0], case=False, na=False)].head(3)

        item = {
            "Наименование из ТЗ": name,
            "Кол-во": qty
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

    # Формирование Excel-выхода
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

    return ts_text, result_df, output.read()
