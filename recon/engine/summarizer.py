"""核对结果摘要。"""


def summarize(differences, left_rows, right_rows):
    return {
        "left_rows": left_rows,
        "right_rows": right_rows,
        "differences": differences,
        "difference_count": len(differences),
        "conclusion": "通过" if not differences else "存在差异",
    }
