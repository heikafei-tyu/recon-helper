from datetime import date
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

    def quote(self, source, target="CNY"):
        return self.convert(1, source, target)

    def update(self, currency, rate):
        value = Decimal(str(rate))
        if value <= 0:
            raise ValueError("汇率必须为正数")
        return FXRates({**self.rates, currency.upper(): value})

    def supported(self):
        return sorted(self.rates)

    def convert_many(self, amounts, source, target="CNY"):
        return [self.convert(amount, source, target) for amount in amounts]

    @staticmethod
    def validate_quotes(quotes, as_of=None, max_age_days=30):
        """Return audit findings for dated quotes: stale and same-day conflicts."""
        if not isinstance(quotes, (list, tuple)):
            raise ValueError("汇率报价必须是列表")
        today = date.fromisoformat(as_of) if as_of else date.today()
        seen = {}
        findings = []
        for quote in quotes:
            try:
                currency = str(quote["currency"]).upper()
                day = date.fromisoformat(str(quote["date"]))
                rate = Decimal(str(quote["rate"]))
            except (KeyError, TypeError, ValueError):
                raise ValueError("汇率报价需要 currency、date、rate 且日期合法") from None
            if rate <= 0:
                raise ValueError("汇率必须为正数")
            key = (currency, day)
            if key in seen and seen[key] != rate:
                findings.append(
                    {
                        "status": "rate_conflict",
                        "currency": currency,
                        "date": str(day),
                        "rates": [str(seen[key]), str(rate)],
                    }
                )
            seen[key] = rate
            if (today - day).days > max_age_days:
                findings.append(
                    {
                        "status": "rate_expired",
                        "currency": currency,
                        "date": str(day),
                        "age_days": (today - day).days,
                        "max_age_days": max_age_days,
                    }
                )
        return findings
