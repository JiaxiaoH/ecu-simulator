# test/test_sequences.py
import pytest
from sequence_loader import load_all_sequences
from testcase_runner import run_sequence, run_excel_case
from tester import Tester
import can
# from excel_io import ExcelTestCases
# excel = ExcelTestCases("testcases.xlsx")
# excel.load()
# excel.cases_to_yaml("testcases.yaml")
# @pytest.mark.parametrize("seq", load_all_sequences())
# def test_sequences(bus, ecu, collector, seq):
#     tester=Tester(bus)
#     run_sequence(seq, bus, collector, ecu, tester)
@pytest.mark.parametrize("case", load_all_sequences())
def test_sequences(bus, runtime, collector, case, excel):
    #tester=Tester(bus)
    ecu, tester, notifier = runtime
    run_excel_case(case, bus, collector, ecu, tester, notifier, excel)