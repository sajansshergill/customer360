from consumer360.connectors.base import BaseConnector

AEM_REQUIRED = ["content_view_id", "email", "device_id", "page_title", "category", "viewed_at"]
COMMERCE_REQUIRED = [
    "order_id",
    "email",
    "sku",
    "product_name",
    "category",
    "quantity",
    "order_total",
    "ordered_at",
]


class AEMCommerceConnector(BaseConnector):
    AEM_FILE = "aem_content.csv"
    COMMERCE_FILE = "commerce_orders.csv"

    def extract_content(self) -> list[dict]:
        rows = self.read_csv(self.AEM_FILE)
        self.validate(rows, AEM_REQUIRED)
        return rows

    def extract_orders(self) -> list[dict]:
        rows = self.read_csv(self.COMMERCE_FILE)
        self.validate(rows, COMMERCE_REQUIRED)
        return rows

    def extract(self) -> list[dict]:
        return self.extract_content()


AEMConnector = AEMCommerceConnector
