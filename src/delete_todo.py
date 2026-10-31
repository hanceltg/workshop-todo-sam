from utils import table, response, publish_event

def handler(event, context):
    todo_id = event["pathParameters"]["id"]
    try:
        result = table.delete_item(
            Key={"id": todo_id},
            ConditionExpression="attribute_exists(id)",
            ReturnValues="ALL_OLD",  # devuelve el TODO borrado
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return response(404, {"message": f"TODO {todo_id} no existe"})

    publish_event("todo.deleted", result["Attributes"])
    return response(204)
