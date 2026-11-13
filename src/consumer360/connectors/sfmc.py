from consumer360.connectors.base import BaseConnector

SFMC_REQUIRED = [
    "event_id",
    "subscriber_key",
    "email",
    "journey_name",
    "event_type",
    "event_at",
    "link_category",
]


class SFMCConnector(BaseConnector):
    FILE = "sfmc_engagement.csv"

    def extract(self) -> list[dict]:
        rows = self.read_csv(self.FILE)
        self.validate(rows, SFMC_REQUIRED)
        return rows
