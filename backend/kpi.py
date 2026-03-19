from typing import List, Dict, Any
import json, re

class KPI:
    # Standardizes the important KPI's format when parsed from earnings calls

    def __init__(self, kpi: str, value: float, unit: str):
        # Stores the metric name, numerical value, and unit of measurement
        self.kpi = kpi
        self.value = value
        self.unit = unit

    def to_dict(self):
        # Converts the KPI object attributes into a standard dictionary format
        return {"kpi": self.kpi, "value": self.value, "unit": self.unit}