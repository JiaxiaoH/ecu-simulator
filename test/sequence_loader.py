# test/sequence_loader.py
import csv
import yaml
from excel_io import ExcelTestCases
def load_sequences_from_csv(path="test/testcases.csv"):
    sequences = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tc_id = row["TestCaseID"]
            if tc_id not in sequences:
                sequences[tc_id] = {"TestCaseID": tc_id, "Steps": []}

            step = {
                "Action": row["Action"].strip(),
                "Request": row.get("Request", "").strip(),
                "Expected": row.get("Expected", "").strip(),
                "VarName": row.get("VarName", "").strip(),
                "SeedVar": row.get("SeedVar", "").strip()
            }

            sequences[tc_id]["Steps"].append(step)

    return list(sequences.values())


def load_sequences_from_yaml(path="test/testcases.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_all_sequences():
    seqs = []

    try:
        seqs += load_sequences_from_yaml()
    except FileNotFoundError:
        pass

    try:
        seqs += load_sequences_from_csv()
    except FileNotFoundError:
        pass

    try:
        excel = ExcelTestCases("testcases.xlsx")
        excel.load()
        seqs= excel.cases
    except FileNotFoundError:
        pass
    
    return seqs
