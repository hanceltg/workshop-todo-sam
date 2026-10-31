import json

def handler(event, context):
    """Consume eventos todo.completed de NotificationsQueue."""
    failures = []
    for record in event["Records"]:
        attempt = record.get("attributes", {}).get("ApproximateReceiveCount", "?")
        try:
            evt = json.loads(record["body"])
            todo = evt["data"]

            # Mensaje "venenoso" simulado para practicar reintentos y DLQ
            # if "#fail" in todo["title"]:
                # raise ValueError("fallo simulado: el título contiene #fail")

            print(f'[NOTIFICACION] Completado: "{todo["title"]}" ({todo["id"]})')
        except Exception as exc:
            print(f'[ERROR] mensaje {record["messageId"]} intento {attempt}: {exc}')
            failures.append({"itemIdentifier": record["messageId"]})

    return {"batchItemFailures": failures}
