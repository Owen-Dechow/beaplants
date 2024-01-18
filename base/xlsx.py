from typing import Any
import xlsxwriter as xl
from xlsxwriter.worksheet import Worksheet


class Workbook:
    workbook: xl.Workbook
    sheets: dict[str, Worksheet]

    def __init__(self, name: str, sheets: list[str]):
        self.workbook = xl.Workbook(name, {"in_memory": True})
        self.sheets = {}
        for key in sheets:
            self.sheets[key] = self.workbook.add_worksheet(key)

    def write_sheet(self, sheet_name: str, cols: list[str], objs: list[Any]):
        sheet = self.sheets[sheet_name]
        sheet.write_row(0, 0, cols)
        for idx, obj in enumerate(objs):
            sheet.write_row(idx + 1, 0, [getattr(obj, x).__str__() for x in cols])

        sheet.freeze_panes(1, 0)

    def close(self):
        self.workbook.close()
