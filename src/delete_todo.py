from utils import table, response

def handler(event, context):
    todo_id = event["pathParameters"]["id"]
    try:
        table.delete_item(
            Key={"id": todo_id},
            ConditionExpression="attribute_exists(id)",
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return response(404, {"message": f"TODO {todo_id} no existe"})

    return response(204)
