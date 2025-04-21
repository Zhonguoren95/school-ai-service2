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
def process_documents(spec_file, prices_files, discounts_file=None):
    from io import BytesIO
    import pandas as pd
    from openpyxl import load_workbook
    from difflib import SequenceMatcher

    # 1. Распознать текст из ТЗ
    ts_text = extract_text_from_pdf(spec_file)
    ts_df = parse_requirements(ts_text)

    # 2. Загрузить прайсы
    price_df = load_price_list(prices_files)

    # 3. Загрузить скидки
    discounts = {}
    if discounts_file is not None:
        df = pd.read_excel(discounts_file)
        for _, row in df.iterrows():
            supplier = str(row[0]).strip()
            try:
                discount = float(row[1])
                discounts[supplier] = discount
            except:
                pass

    # 4. Поиск совпадений
    results = []
    for _, row in ts_df.iterrows():
        name = row["Наименование"]
        qty = row["Кол-во"]

        # Поиск похожих позиций
        matches = []
        for _, p_row in price_df.iterrows():
            pname = str(p_row["Наименование"]).lower()
            score = SequenceMatcher(None, name.lower(), pname).ratio()
            if score > 0.4:
                matches.append((score, p_row))

        matches = sorted(matches, key=lambda x: -x[0])[:3]  # топ-3

        item = {
            "Наименование из ТЗ": name,
            "Кол-во": qty,
        }

        for i, (score, match_row) in enumerate(matches):
            price = match_row["Цена"]
            supplier = match_row.get("Поставщик", f"Поставщик {i+1}")
            discount = discounts.get(supplier, 0)
            final_price = round(price * (1 - discount / 100), 2) if price else ""

            item[f"Поставщик {i+1}"] = supplier
            item[f"Цена {i+1}"] = price
            item[f"Скидка {i+1}"] = f"{discount}%"
            item[f"Итог {i+1}"] = final_price

        results.append(item)

    result_df = pd.DataFrame(results)

    # 5. Записать в Excel
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
        ws.cell(row=start_row + i, column=7, value=row.get("Итог 1")
   def process_documents(spec_file, prices_files, discounts_file=None):
    from io import BytesIO
    import pandas as pd
    from openpyxl import load_workbook
    from difflib import SequenceMatcher

    # 1. Распознать текст из ТЗ
    ts_text = extract_text_from_pdf(spec_file)
    ts_df = parse_requirements(ts_text)

    # 2. Загрузить прайсы
    price_df = load_price_list(prices_files)

    # 3. Загрузить скидки
    discounts = {}
    if discounts_file is not None:
        df = pd.read_excel(discounts_file)
        for _, row in df.iterrows():
            supplier = str(row[0]).strip()
            try:
                discount = float(row[1])
                discounts[supplier] = discount
            except:
                pass

    # 4. Поиск совпадений
    results = []
    for _, row in ts_df.iterrows():
        name = row["Наименование"]
        qty = row["Кол-во"]

        # Поиск похожих позиций
        matches = []
        for _, p_row in price_df.iterrows():
            pname = str(p_row["Наименование"]).lower()
            score = SequenceMatcher(None, name.lower(), pname).ratio()
            if score > 0.4:
                matches.append((score, p_row))

        matches = sorted(matches, key=lambda x: -x[0])[:3]  # топ-3

        item = {
            "Наименование из ТЗ": name,
            "Кол-во": qty,
        }

        for i, (score, match_row) in enumerate(matches):
            price = match_row["Цена"]
            supplier = match_row.get("Поставщик", f"Поставщик {i+1}")
            discount = discounts.get(supplier, 0)
            final_price = round(price * (1 - discount / 100), 2) if price else ""

            item[f"Поставщик {i+1}"] = supplier
            item[f"Цена {i+1}"] = price
            item[f"Скидка {i+1}"] = f"{discount}%"
            item[f"Итог {i+1}"] = final_price

        results.append(item)

    result_df = pd.DataFrame(results)

    # 5. Записать в Excel
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

