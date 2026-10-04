import json
from pathlib import Path
from recon.engine import run_rules
print(json.dumps(run_rules(Path(__file__).with_name("rules.yaml")), ensure_ascii=False, indent=2))
