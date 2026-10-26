from utils import table, response

def handler(event, context):
    items = []
    kwargs = {}
    while True:
        result = table.scan(**kwargs)
        items.extend(result.get("Items", []))
        if "LastEvaluatedKey" not in result:
            break
        kwargs["ExclusiveStartKey"] = result["LastEvaluatedKey"]

    items.sort(key=lambda t: t["createdAt"])
    return response(200, items)
