import json
from pathlib import Path
from recon.notify import NotificationSettings, notify_result

class Response:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *_): return False

def test_notification_scenario():
    config = __import__("yaml").safe_load((Path(__file__).parent / "notification_demo" / "config.yaml").read_text())
    requests = []
    def opener(request, timeout): requests.append(json.loads(request.data)); return Response()
    result = notify_result({"differences": [{"status": "left_only"}]}, NotificationSettings(**config), opener=opener)
    assert result["sent"] and requests[0]["summary"]["fatal"] == 1
