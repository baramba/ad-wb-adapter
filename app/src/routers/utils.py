class CommonQueryParams:
    def __init__(
        self, routing_key: str, wb_token: str, wb_user_id: int, wb_supplier_id: str
    ):
        self.routing_key = routing_key
        self.wb_token = wb_token
        self.wb_user_id = wb_user_id
        self.wb_supplier_id = wb_supplier_id
