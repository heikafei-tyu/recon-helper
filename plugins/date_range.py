from datetime import date

def check(left, right, rule):
    start = date.fromisoformat(rule["start"])
    end = date.fromisoformat(rule["end"])
    output = []
    for index, value in enumerate([*left, *right]):
        parsed = date.fromisoformat(str(value))
        if not start <= parsed <= end:
            output.append({"status": "date_out_of_range", "index": index, "value": str(value)})
    return output
