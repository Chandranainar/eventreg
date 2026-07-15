from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: int
    admin_user_id: int | None
    action: str
    entity_type: str
    entity_id: str
    old_values: dict | None
    new_values: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
