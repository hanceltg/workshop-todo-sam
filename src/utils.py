import json
import os
from decimal import Decimal
import boto3

TABLE_NAME = os.environ["TABLE_NAME"]
table = boto3.resource("dynamodb").Table(TABLE_NAME)

def _default(obj):
    # DynamoDB devuelve los números como Decimal
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"Tipo no serializable: {type(obj)}")

def response(status, body=None):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, default=_default) if body is not None else "",
    }

def parse_body(event):
    """Devuelve el body como dict, o None si no es JSON válido."""
    try:
        return json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return None
