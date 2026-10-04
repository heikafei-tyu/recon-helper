def check(left, right, rule):
    left_total = sum(float(value) for value in left)
    right_total = sum(float(value) for value in right)
    difference = left_total - right_total
    return (
        []
        if difference == 0
        else [
            {"status": "sum_mismatch", "left_total": left_total, "right_total": right_total, "difference": difference}
        ]
    )
