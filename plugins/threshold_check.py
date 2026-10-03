def check(left, right, rule):
    threshold = float(rule.get("threshold", 0))
    output = []
    for index, (a, b) in enumerate(zip(left, right)):
        delta = abs(float(a) - float(b))
        if delta > threshold:
            output.append({"status": "threshold_exceeded", "index": index, "difference": delta, "threshold": threshold})
    return output
