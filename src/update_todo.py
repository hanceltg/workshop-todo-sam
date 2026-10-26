from datetime import datetime, timezone
from utils import table, response, parse_body

def handler(event, context):
    todo_id = event["pathParameters"]["id"]
    data = parse_body(event)
    if data is None:
        return response(400, {"message": "El body debe ser JSON válido"})

    sets = ["updatedAt = :u"]
    values = {":u": datetime.now(timezone.utc).isoformat()}
    names = {}

    if "title" in data:
        title = str(data["title"]).strip()
        if not title:
            return response(400, {"message": "'title' no puede estar vacío"})
        sets.append("#t = :t")
        names["#t"] = "title"
        values[":t"] = title

    if "completed" in data:
        if not isinstance(data["completed"], bool):
            return response(400, {"message": "'completed' debe ser true/false"})
        sets.append("completed = :c")
        values[":c"] = data["completed"]

    if len(sets) == 1:
        return response(400, {"message": "Envía 'title' y/o 'completed'"})

    kwargs = {
        "Key": {"id": todo_id},
        "UpdateExpression": "SET " + ", ".join(sets),
        "ExpressionAttributeValues": values,
        "ConditionExpression": "attribute_exists(id)",
        "ReturnValues": "ALL_NEW",
    }
    if names:
        kwargs["ExpressionAttributeNames"] = names

    try:
        result = table.update_item(**kwargs)
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return response(404, {"message": f"TODO {todo_id} no existe"})

    return response(200, result["Attributes"])
