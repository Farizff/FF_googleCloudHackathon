from agent.tools.notify_contacts import notify_contacts


class FakeContactsCollection:
    def __init__(self, contacts):
        self.contacts = contacts
        self.queries = []

    def find(self, query):
        self.queries.append(query)
        return [contact for contact in self.contacts if contact.get("trip_id") == query.get("trip_id")]


class FakeLogCollection:
    def __init__(self):
        self.inserted = []

    def insert_one(self, document):
        self.inserted.append(document)


def test_notify_contacts_sends_to_all_contacts_and_logs_successes():
    contacts = FakeContactsCollection(
        [
            {"trip_id": "trip_tokyo", "name": "Maya", "email": "maya@example.com", "detail_level": "summary", "language": "en"},
            {"trip_id": "trip_tokyo", "name": "Omar", "email": "omar@example.com", "detail_level": "updates_only", "language": "en"},
        ]
    )
    logs = FakeLogCollection()
    sent_messages = []

    def send_email(to_email, subject, body):
        sent_messages.append({"to_email": to_email, "subject": subject, "body": body})
        return {"message_id": f"msg_{len(sent_messages)}"}

    result = notify_contacts(
        trip_id="trip_tokyo",
        trigger_event="venue_closure",
        notification_context={"event_description": "teamLab closed", "changes_summary": "Mori Art Museum added."},
        contacts_collection=contacts,
        notification_log_collection=logs,
        send_email_fn=send_email,
        clock=lambda: "2026-07-11T09:30:00Z",
    )

    assert result == {"sent": 2, "failed": 0}
    assert contacts.queries == [{"trip_id": "trip_tokyo"}]
    assert [message["to_email"] for message in sent_messages] == ["maya@example.com", "omar@example.com"]
    assert all(message["subject"] == "Bounce trip update: venue closure" for message in sent_messages)
    assert [log["status"] for log in logs.inserted] == ["sent", "sent"]
    assert logs.inserted[0]["message_id"] == "msg_1"


def test_notify_contacts_accounts_for_failed_sends_and_logs_error():
    contacts = FakeContactsCollection(
        [{"trip_id": "trip_tokyo", "name": "Maya", "email": "maya@example.com", "detail_level": "summary", "language": "en"}]
    )
    logs = FakeLogCollection()

    def send_email(to_email, subject, body):
        raise RuntimeError("SendGrid rejected recipient")

    result = notify_contacts(
        "trip_tokyo",
        "flight_delay",
        {"event_description": "NH106 delayed", "changes_summary": "Pickup shifted 40 minutes."},
        contacts,
        logs,
        send_email,
        clock=lambda: "2026-07-11T09:30:00Z",
    )

    assert result == {"sent": 0, "failed": 1}
    assert logs.inserted == [
        {
            "trip_id": "trip_tokyo",
            "email": "maya@example.com",
            "trigger_event": "flight_delay",
            "status": "failed",
            "sent_at": "2026-07-11T09:30:00Z",
            "error": "SendGrid rejected recipient",
        }
    ]


def test_notify_contacts_detail_level_changes_message_body():
    contacts = FakeContactsCollection(
        [
            {"trip_id": "trip_tokyo", "name": "Full", "email": "full@example.com", "detail_level": "full", "language": "en"},
            {"trip_id": "trip_tokyo", "name": "Summary", "email": "summary@example.com", "detail_level": "summary", "language": "en"},
            {"trip_id": "trip_tokyo", "name": "Updates", "email": "updates@example.com", "detail_level": "updates_only", "language": "en"},
        ]
    )
    bodies = []

    notify_contacts(
        "trip_tokyo",
        "venue_closure",
        {"event_description": "teamLab closed", "changes_summary": "Mori Art Museum added."},
        contacts,
        FakeLogCollection(),
        lambda to_email, subject, body: bodies.append(body) or {"message_id": to_email},
        clock=lambda: "2026-07-11T09:30:00Z",
    )

    assert "What happened: teamLab closed" in bodies[0]
    assert "What changed: Mori Art Museum added." in bodies[0]
    assert "What changed: Mori Art Museum added." in bodies[1]
    assert "What happened:" not in bodies[1]
    assert bodies[2] == "Bounce update: Mori Art Museum added."


def test_notify_contacts_translates_non_english_contacts_when_translator_provided():
    contacts = FakeContactsCollection(
        [{"trip_id": "trip_tokyo", "name": "Lucia", "email": "lucia@example.com", "detail_level": "updates_only", "language": "es"}]
    )
    translate_calls = []
    sent_bodies = []

    def translate(text, target_language):
        translate_calls.append({"text": text, "target_language": target_language})
        return f"[es]{text}"

    notify_contacts(
        "trip_tokyo",
        "venue_closure",
        {"event_description": "teamLab closed", "changes_summary": "Mori Art Museum added."},
        contacts,
        FakeLogCollection(),
        lambda to_email, subject, body: sent_bodies.append(body) or {"message_id": "msg_es"},
        translate_fn=translate,
        clock=lambda: "2026-07-11T09:30:00Z",
    )

    assert translate_calls == [{"text": "Bounce update: Mori Art Museum added.", "target_language": "es"}]
    assert sent_bodies == ["[es]Bounce update: Mori Art Museum added."]


def test_notify_contacts_returns_zero_counts_for_empty_contacts():
    logs = FakeLogCollection()

    result = notify_contacts(
        "trip_tokyo",
        "venue_closure",
        {"event_description": "teamLab closed", "changes_summary": "Mori Art Museum added."},
        FakeContactsCollection([]),
        logs,
        lambda to_email, subject, body: {"message_id": "unused"},
        clock=lambda: "2026-07-11T09:30:00Z",
    )

    assert result == {"sent": 0, "failed": 0}
    assert logs.inserted == []
