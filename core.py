import pandas as pd
import fitz  # PyMuPDF
import re
from openpyxl import load_workbook
from io import BytesIO

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def parse_requirements(text):
    lines = text.split("\n")
    rows = []
    for line in lines:
        if any(char.isdigit() for char in line):
            parts = re.split(r"\s{2,}|	", line.strip())
            if len(parts) >= 2:
                name = parts[0]
                quantity = re.search(r"\d+", parts[1])
                quantity = quantity.group() if quantity else ""
                rows.append({"Наименование": name, "Кол-во": quantity})
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
    if not file:
        return {}
    df = pd.read_excel(file)
    return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

def find_matches(requirements_df, price_df, discounts):
    results = []
    for _, req in requirements_df.iterrows():
        name = req["Наименование"].lower()
        quantity = int(req["Кол-во"])
        matches = price_df[price_df["Наименование"].str.lower().str.contains(name.split()[0])]
        for _, match in matches.head(3).iterrows():
            supplier = match.get("Поставщик", "")
            price = match.get("Цена", 0)
            discount = discounts.get(supplier, 0)
            price_with_discount = price * (1 - discount / 100)
            results.append({
                "Позиция из ТЗ": req["Наименование"],
                "Кол-во": quantity,
                "Совпадение": match["Наименование"],
                "Цена": price,
                "Цена со скидкой": round(price_with_discount, 2),
                "Поставщик": supplier
            })
    return pd.DataFrame(results)

def fill_result_template(df_result, template_file):
    wb = load_workbook(template_file)
    ws = wb.active
    start_row = 5
    for idx, row in df_result.iterrows():
        ws.cell(row=start_row + idx, column=1, value=row["Позиция из ТЗ"])
        ws.cell(row=start_row + idx, column=2, value=row["Кол-во"])
        ws.cell(row=start_row + idx, column=3, value=row["Совпадение"])
        ws.cell(row=start_row + idx, column=4, value=row["Цена"])
        ws.cell(row=start_row + idx, column=5, value=row["Цена со скидкой"])
        ws.cell(row=start_row + idx, column=6, value=row["Поставщик"])
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def process_documents(ts_file, price_files, discount_file=None):
    ts_text = extract_text_from_pdf(ts_file)
    requirements_df = parse_requirements(ts_text)
    price_df = load_price_list(price_files)
    discounts = load_discounts(discount_file)
    result_df = find_matches(requirements_df, price_df, discounts)
    result_file = fill_result_template(result_df, "Форма для результата.xlsx")
    return ts_text, result_df, result_file
