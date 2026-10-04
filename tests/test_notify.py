import json

import pytest

from recon.notify import NotificationSettings, notify_result


class _Response:
    status = 204

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class _SMTP:
    instances = []

    def __init__(self, host, port, timeout):
        self.sent = []
        self.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def send_message(self, message):
        self.sent.append(message)


def test_webhook_sends_json_summary():
    requests = []

    def opener(request, timeout):
        requests.append((request, timeout))
        return _Response()

    result = notify_result(
        {"differences": [{"status": "mismatch"}]},
        NotificationSettings("https://example.test/hook", enabled=True),
        opener=opener,
    )
    assert result["sent"] and result["channels"]["webhook"]["status"] == 204
    assert json.loads(requests[0][0].data)["summary"]["serious"] == 1


def test_fatal_forces_notification_when_disabled():
    calls = []
    result = notify_result(
        {"differences": [{"status": "left_only"}]},
        NotificationSettings("https://example.test", enabled=False),
        opener=lambda request, timeout: calls.append(request) or _Response(),
    )
    assert result["sent"] and len(calls) == 1


def test_smtp_sends_message():
    _SMTP.instances.clear()
    result = notify_result(
        {"differences": []},
        NotificationSettings(smtp_host="smtp.test", smtp_to="ops@test", smtp_from="bot@test", enabled=True),
        smtp_factory=_SMTP,
    )
    assert result["sent"] and _SMTP.instances[0].sent[0]["To"] == "ops@test"


def test_disabled_without_fatal_does_not_send():
    result = notify_result({"differences": []}, NotificationSettings(enabled=False))
    assert result["sent"] is False and result["channels"] == {}


@pytest.mark.parametrize("settings", [None, object()])
def test_invalid_settings_rejected(settings):
    with pytest.raises(TypeError):
        notify_result({}, settings)
