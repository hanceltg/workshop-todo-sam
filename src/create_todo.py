import uuid
from datetime import datetime, timezone
from utils import table, response, parse_body, publish_event

def handler(event, context):
    data = parse_body(event)
    if data is None:
        return response(400, {"message": "El body debe ser JSON válido"})

    title = str(data.get("title", "")).strip()
    if not title:
        return response(400, {"message": "El campo 'title' es obligatorio"})

    now = datetime.now(timezone.utc).isoformat()
    item = {
        "id": str(uuid.uuid4()),
        "title": title,
        "completed": False,
        "createdAt": now,
        "updatedAt": now,
    }
    table.put_item(Item=item)
    publish_event("todo.created", item)
    return response(201, item)
