from consumer360.connectors.base import BaseConnector

CDC_REQUIRED = [
    "cdc_id",
    "email",
    "first_name",
    "last_name",
    "phone",
    "date_of_birth",
    "city",
    "zip_code",
    "is_professional",
    "speciality",
    "marketing_consent",
    "profiling_consent",
    "third_party_sharing",
    "registered_at",
]


class SAPCDCConnector(BaseConnector):
    FILE = "sap_cdc_profiles.csv"

    def extract(self) -> list[dict]:
        rows = self.read_csv(self.FILE)
        self.validate(rows, CDC_REQUIRED)
        return rows
