import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
import boto3

TABLE_NAME = os.environ["TABLE_NAME"]
table = boto3.resource("dynamodb").Table(TABLE_NAME)

# Parte 2: topic de eventos y tabla de auditoría
TOPIC_ARN = os.environ.get("TOPIC_ARN", "")
AUDIT_TABLE_NAME = os.environ.get("AUDIT_TABLE_NAME", "")
audit_table = boto3.resource("dynamodb").Table(AUDIT_TABLE_NAME)
sns = boto3.client("sns")

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

def publish_event(event_type, todo):
    """Publica un evento de dominio en el topic SNS."""
    event = {
        "eventId": str(uuid.uuid4()),
        "eventType": event_type,
        "occurredAt": datetime.now(timezone.utc).isoformat(),
        "source": "todos-api",
        "data": todo,
    }
    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=json.dumps(event, default=_default),
        # El atributo permite que SNS filtre sin abrir el mensaje
        MessageAttributes={
            "eventType": {"DataType": "String", "StringValue": event_type}
        },
    )
    return event
