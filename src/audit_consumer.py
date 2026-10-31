import json
from decimal import Decimal
from utils import audit_table

def handler(event, context):
    """Consume eventos de AuditQueue y los guarda en AuditTable."""
    failures = []
    for record in event["Records"]:
        try:
            evt = json.loads(record["body"], parse_float=Decimal)
            audit_table.put_item(
                Item={
                    "todoId": evt["data"]["id"],
                    # occurredAt#eventId => orden cronológico + idempotencia
                    "sk": f'{evt["occurredAt"]}#{evt["eventId"]}',
                    "eventId": evt["eventId"],
                    "eventType": evt["eventType"],
                    "occurredAt": evt["occurredAt"],
                    "snapshot": evt["data"],
                }
            )
            print(f'[AUDIT] {evt["eventType"]} -> {evt["data"]["id"]}')
        except Exception as exc:
            print(f'[ERROR] mensaje {record["messageId"]}: {exc}')
            failures.append({"itemIdentifier": record["messageId"]})

    # Solo se reintentan los mensajes que fallaron
    return {"batchItemFailures": failures}
