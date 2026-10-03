import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def _digest(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_snapshot(rules_file, result, directory="history"):
    rules_path = Path(rules_file)
    data = json.loads(rules_path.read_text(encoding="utf-8-sig")) if rules_path.suffix == ".json" else rules_path.read_text(encoding="utf-8-sig")
    source = data if isinstance(data, dict) else {}
    files = [rules_path]
    for key in ("left", "right"):
        if source.get(key):
            files.append(rules_path.parent / source[key])
    snapshot = {"created_at": datetime.now(timezone.utc).isoformat(), "rules": source, "files": {str(path): _digest(path) for path in files if path.exists()}, "summary": {"differences": len(result.get("differences", [])), "left_rows": result.get("left_rows", 0), "right_rows": result.get("right_rows", 0)}, "differences": result.get("differences", [])}
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def list_history(directory="history"):
    return sorted(Path(directory).glob("*.json"))


def load_history(directory="history"):
    return [json.loads(path.read_text(encoding="utf-8")) for path in list_history(directory)]


def compare_snapshots(before, after):
    """Compare two snapshot dictionaries by their serialized difference entries."""
    def differences(snapshot):
        value = snapshot.get("differences", [])
        return {json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value}
    old, new = differences(before), differences(after)
    return {"added": [json.loads(item) for item in sorted(new - old)], "resolved": [json.loads(item) for item in sorted(old - new)], "unchanged": len(old & new)}


def compare_history(directory, before, after):
    records = load_history(directory)
    try:
        left, right = records[before], records[after]
    except IndexError as exc:
        raise ValueError("历史记录索引超出范围") from exc
    return compare_snapshots(left, right)
