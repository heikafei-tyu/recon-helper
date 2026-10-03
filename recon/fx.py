from decimal import Decimal


class FXRates:
    def __init__(self, rates=None):
        self.rates = {"CNY": Decimal("1"), **{key.upper(): Decimal(str(value)) for key, value in (rates or {}).items()}}
        if any(value <= 0 for value in self.rates.values()):
            raise ValueError("汇率必须为正数")
    def convert(self, amount, source, target="CNY"):
        source, target = source.upper(), target.upper()
        if source not in self.rates or target not in self.rates:
            raise ValueError(f"未配置汇率：{source} 或 {target}")
        return Decimal(str(amount)) * self.rates[source] / self.rates[target]
    def convert_rows(self, rows, column, source, target="CNY"):
        return [{**row, column: str(self.convert(row[column], source, target))} for row in rows]
