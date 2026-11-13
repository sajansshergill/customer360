from consumer360.connectors.base import BaseConnector

GA4_REQUIRED = [
    "event_id",
    "device_id",
    "user_pseudo_id",
    "email",
    "session_id",
    "event_name",
    "item_name",
    "event_at",
]


class GA4Connector(BaseConnector):
    FILE = "ga4_events.csv"

    def extract(self) -> list[dict]:
        rows = self.read_csv(self.FILE)
        self.validate(rows, GA4_REQUIRED)
        return rows
