from boto3.dynamodb.conditions import Key
from utils import audit_table, response

def handler(event, context):
    todo_id = event["pathParameters"]["id"]

    # Query (no Scan): lee solo la partición de este TODO, ya ordenada por sk
    items = []
    kwargs = {"KeyConditionExpression": Key("todoId").eq(todo_id)}
    while True:
        result = audit_table.query(**kwargs)
        items.extend(result.get("Items", []))
        if "LastEvaluatedKey" not in result:
            break
        kwargs["ExclusiveStartKey"] = result["LastEvaluatedKey"]

    history = [
        {"eventType": i["eventType"], "occurredAt": i["occurredAt"], "snapshot": i["snapshot"]}
        for i in items
    ]
    return response(200, history)
