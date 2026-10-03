"""独立的 Decimal 容差判断。"""
from decimal import Decimal


def within_tolerance(left, right, absolute=0, relative=0):
    left, right = Decimal(str(left)), Decimal(str(right))
    delta = abs(left - right)
    threshold = max(Decimal(str(absolute)), max(abs(left), abs(right)) * Decimal(str(relative)))
    return delta <= threshold, delta, threshold
