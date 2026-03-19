import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from kpi import KPI


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

    def test_to_dict_returns_dict(self):
        assert isinstance(KPI("Revenue", 10.0, "billion USD").to_dict(), dict)

    def test_to_dict_has_all_keys(self):
        assert set(KPI("Revenue", 10.0, "billion USD").to_dict().keys()) == {"kpi", "value", "unit"}

    def test_to_dict_values(self):
        d = KPI("Operating Income", 3.2, "billion USD").to_dict()
        assert d == {"kpi": "Operating Income", "value": 3.2, "unit": "billion USD"}

    def test_to_dict_roundtrip(self):
        d = KPI("Free Cash Flow", 7.8, "billion USD").to_dict()
        assert KPI(**d).to_dict() == d

    def test_to_dict_empty_strings(self):
        assert KPI("", 0.0, "").to_dict() == {"kpi": "", "value": 0.0, "unit": ""}