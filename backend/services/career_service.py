import pandas as pd

excel_path = "data/careers.xlsx"


def load_careers():
    df = pd.read_excel(excel_path, header=None)

    careers = {
        "science": [],
        "commerce": [],
        "arts": [],
        "vocational": [],
        "government": [],
        "other": []
    }

    # ── Helper: standard layout (arts / commerce / science / other / vocational) ──
    def extract_standard(start_row, end_row, col_name=1, col_duration=2, col_exam=3,
                         col_fee=5, col_jobs=6, col_salary=7):
        results = []
        for i in range(start_row + 1, end_row):
            row = df.iloc[i]
            sr = str(row[0]).strip() if pd.notna(row[0]) else ""
            if not sr or sr.lower() == "nan" or not sr.replace(".", "").isdigit():
                continue
            try:
                item = {
                    "course":      str(row[col_name]).strip()     if pd.notna(row[col_name])     else "",
                    "duration":    str(row[col_duration]).strip()  if pd.notna(row[col_duration]) else "",
                    "exam":        str(row[col_exam]).strip()      if pd.notna(row[col_exam])     else "",
                    "course_fee":  str(row[col_fee]).strip()       if pd.notna(row[col_fee])      else "",
                    "jobs":        str(row[col_jobs]).strip()      if pd.notna(row[col_jobs])     else "",
                    "salary":      str(row[col_salary]).strip()    if pd.notna(row[col_salary])   else "",
                }
                if item["course"] and item["course"].lower() != "nan":
                    results.append(item)
            except Exception:
                pass
        return results

    # ── Helper: vocational / other layout ──
    # cols: 1=name  4=duration  6=exam  5=fee  7=jobs  8=salary
    def extract_vocational(start_row, end_row):
        return extract_standard(start_row, end_row,
                                col_name=1, col_duration=4, col_exam=6,
                                col_fee=5, col_jobs=7, col_salary=8)

    # ── Helper: government layout ──
    # cols: 2=job  9=training period  3=exam  5=exam-fee  1=sector  8=exam-levels
    def extract_government(start_row, end_row):
        results = []
        for i in range(start_row + 1, end_row):
            row = df.iloc[i]
            sr = str(row[0]).strip() if pd.notna(row[0]) else ""
            if not sr or sr.lower() == "nan" or not str(sr).replace(".", "").isdigit():
                continue
            try:
                item = {
                    "course":     str(row[2]).strip() if pd.notna(row[2]) else "",   # job title
                    "duration":   str(row[9]).strip() if pd.notna(row[9]) else "",   # training period
                    "exam":       str(row[3]).strip() if pd.notna(row[3]) else "",   # exam name
                    "course_fee": str(row[5]).strip() if pd.notna(row[5]) else "",   # exam fee
                    "jobs":       str(row[1]).strip() if pd.notna(row[1]) else "",   # sector
                    "salary":     str(row[4]).strip() if pd.notna(row[4]) else "",   # age limit info
                }
                if item["course"] and item["course"].lower() != "nan":
                    results.append(item)
            except Exception:
                pass
        return results

    # ── Section boundaries (row indices from Excel) ──
    # 0   = ARTS
    # 146 = COMMERCE
    # 235 = SCIENCE
    # 415 = VOCATIONAL & TECHNICAL
    # 620 = STATE GOVERNMENT JOBS
    # 675 = CENTRAL GOVERNMENT JOBS
    # 730 = OTHER CREATIVE & TECH FIELDS
    # 846 = CAREER & SALARY SUMMARY (end)

    careers["arts"]       = extract_standard(0,   146)
    careers["commerce"]   = extract_standard(146, 235)
    careers["science"]    = extract_standard(235, 415)
    careers["vocational"] = extract_vocational(415, 620)
    careers["government"] = extract_government(620, 675) + extract_government(675, 730)
    careers["other"]      = extract_vocational(730, 846)

    return careers


# Load once at startup
all_careers = load_careers()


def get_career_by_stream(stream: str) -> list:
    stream = stream.lower().strip()
    return all_careers.get(stream, [])