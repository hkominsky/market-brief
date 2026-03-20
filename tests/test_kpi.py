import os
import sys
from kpi import KPI

sys.path.insert(0, os.path.dirname(__file__))

class TestKPI:
    def test_stores_kpi_name(self):
        assert KPI("Revenue", 1.5, "billion USD").kpi == "Revenue"

    def test_stores_value(self):
        assert KPI("EPS", 2.34, "USD").value == 2.34

    def test_stores_unit(self):
        assert KPI("Gross Margin", 42.1, "%").unit == "%"

    def test_zero_value(self):
        assert KPI("Net Income", 0, "million USD").value == 0

    def test_negative_value(self):
        assert KPI("Net Loss", -500.0, "million USD").value == -500.0

    def test_float_precision(self):
        assert KPI("EPS", 1.123456789, "USD").value == 1.123456789

    def test_large_value(self):
        assert KPI("Market Cap", 3_000_000_000_000.0, "USD").value == 3e12

    def test_empty_strings_allowed(self):
        k = KPI("", 0.0, "")
        assert k.kpi == "" and k.unit == ""

    def test_returns_dict(self):
        assert isinstance(KPI("Revenue", 10.0, "billion USD").to_dict(), dict)

    def test_has_all_keys(self):
        assert set(KPI("Revenue", 10.0, "billion USD").to_dict().keys()) == {"kpi", "value", "unit"}

    def test_values_correct(self):
        d = KPI("Operating Income", 3.2, "billion USD").to_dict()
        assert d == {"kpi": "Operating Income", "value": 3.2, "unit": "billion USD"}

    def test_roundtrip(self):
        d = KPI("Free Cash Flow", 7.8, "billion USD").to_dict()
        assert KPI(**d).to_dict() == d

    def test_negative_value_in_dict(self):
        assert KPI("Net Loss", -5.0, "USD").to_dict()["value"] == -5.0

    def test_zero_in_dict(self):
        assert KPI("Metric", 0.0, "units").to_dict()["value"] == 0.0
