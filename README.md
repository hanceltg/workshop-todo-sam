# Workshop: CRUD de TODOs con AWS SAM (Python)

**Autor:** Hance L. · **Curso:** Programación Agéntica

API REST serverless para gestionar una lista de tareas, definida 100% como código con AWS SAM y desplegada en mi propia cuenta de AWS.

## Arquitectura

```
Cliente (curl / Postman / PowerShell)
        │
   API Gateway (REST, stage dev)
        │
 ┌──────┼───────┬───────────┬────────────┐
Create  List   Get       Update       Delete     ← 5 funciones Lambda (python3.13)
        └──────┴───────┴────────────┘
                     │
                DynamoDB (TodosTable, PAY_PER_REQUEST)
```

| Método | Ruta | Respuesta OK | Errores |
|---|---|---|---|
| POST | `/todos` | 201 + TODO creado | 400 |
| GET | `/todos` | 200 + lista | — |
| GET | `/todos/{id}` | 200 + TODO | 404 |
| PUT | `/todos/{id}` | 200 + TODO actualizado | 400, 404 |
| DELETE | `/todos/{id}` | 204 sin contenido | 404 |

## Estructura del proyecto

```
todo-sam/
├── template.yaml        # infraestructura
├── samconfig.toml       # configuración de deploy
├── src/
│   ├── utils.py         # cliente DynamoDB, response(), parse_body()
│   ├── create_todo.py
│   ├── list_todos.py
│   ├── get_todo.py
│   ├── update_todo.py
│   └── delete_todo.py
└── capturas/            # evidencias de la entrega
```

## Cómo desplegar

```powershell
sam validate --lint
sam build
sam deploy --guided
```

Datos de mi despliegue: stack `todo-sam-hance`, región `us-east-2` (Ohio).

## Cómo probar

```powershell
$API = "https://<id>.execute-api.us-east-2.amazonaws.com/dev/todos"

Invoke-RestMethod -Method Post -Uri $API -ContentType "application/json" -Body '{"title": "Estudiar AWS SAM"}'
Invoke-RestMethod -Uri $API
```

## Limpieza

```powershell
sam delete --stack-name todo-sam-hance
```

Verifiqué en CloudFormation que el stack quedó en `DELETE_COMPLETE`.

---

## Qué aprendí

- **Infraestructura como código:** un solo `template.yaml` de unas 120 líneas describe la tabla, la API, las cinco funciones y sus permisos. SAM lo expande a CloudFormation y crea por mí los roles IAM, los permisos de invocación, el deployment y el stage.
- **El ciclo completo:** `sam build` → `sam deploy` → pruebas → logs en CloudWatch → `sam delete`. Tener todo en código hace que crear y destruir el entorno sea reproducible.
- **Mínimo privilegio:** las funciones de lectura usan `DynamoDBReadPolicy` y las de escritura `DynamoDBCrudPolicy`, ambas limitadas a una sola tabla.
- **Arranque en frío:** en los logs de CloudWatch, la primera invocación de `CreateTodoFunction` tardó unos 490 ms (con 463 ms de inicialización) y las siguientes bajaron a 27 y 58 ms.
- **Detalles de DynamoDB:** `title` es palabra reservada y requiere un alias (`#t`); `ConditionExpression` evita que un PUT cree registros por accidente; DynamoDB devuelve números como `Decimal` y hay que convertirlos antes de serializar a JSON.

### Dificultades que resolví

- En **PowerShell 5.1** no existe `&&`, así que ejecuté los comandos uno por línea (o con `;`). Para las pruebas usé `Invoke-RestMethod` y `Invoke-WebRequest` en lugar de `curl`.
- Los archivos de `src/` se crearon vacíos (0 bytes) y los llené antes de hacer el build; si no, las funciones habrían fallado con error 500.
- En `sam deploy --guided`, las preguntas de autenticación de cada función exigen escribir `y`: con Enter el valor por defecto es `N` y el deploy se cancela con `Security Constraints Not Satisfied!`. Las preguntas del archivo y entorno de configuración se aceptan con Enter.
- Mi región configurada era `us-east-2`, no `us-east-1`; tuve que mirar la región correcta en la consola para ver los recursos.

---

## Preguntas de repaso

**1. ¿Por qué las Lambdas no tienen el nombre de la tabla escrito en el código?**
CloudFormation genera el nombre real de la tabla con un sufijo aleatorio (por ejemplo `todo-sam-hance-TodosTable-139TX9R7HN6KX`). El template lo inyecta como variable de entorno `TABLE_NAME` con `!Ref TodosTable`. Así el mismo código funciona en cualquier stack, región o cuenta sin modificarse, y no hay valores duros que se desactualicen.

**2. ¿Qué pasaría en el PUT si quitamos el `ConditionExpression`?**
`update_item` funciona como *upsert*: si el id no existe, DynamoDB crea un ítem nuevo con solo la clave y los campos enviados. El PUT devolvería 200 en vez de 404 y dejaría registros incompletos (sin `createdAt`, y sin `title` si solo se mandó `completed`).

**3. ¿Qué diferencia hay entre `DynamoDBReadPolicy` y `DynamoDBCrudPolicy`, y por qué no darle Crud a todas?**
`DynamoDBReadPolicy` permite solo operaciones de lectura (`GetItem`, `Scan`, `Query`, etc.). `DynamoDBCrudPolicy` agrega escritura y borrado (`PutItem`, `UpdateItem`, `DeleteItem`). Dar Crud a todas rompe el principio de mínimo privilegio: si una función de solo lectura tiene un bug o es comprometida, podría modificar o borrar datos. Lo comprobé comparando los roles `ListTodosFunctionRole` y `CreateTodoFunctionRole` en IAM.

**4. ¿Qué recursos de AWS creó SAM que no escribí explícitamente?**
Cinco roles IAM (uno por función), cinco `AWS::Lambda::Permission` para que API Gateway pueda invocar cada Lambda, la `AWS::ApiGateway::RestApi` subyacente, el `AWS::ApiGateway::Deployment` y el `AWS::ApiGateway::Stage` `dev`. Con CloudFormation puro serían cientos de líneas más.

**5. ¿Cuándo preferiría una Lambda por operación y cuándo una sola?**
*Una por operación* cuando importan los permisos mínimos por función, el escalado y despliegue independientes, paquetes pequeños y logs claros por operación. *Una sola Lambda* cuando se prioriza la simplicidad, menos arranques en frío (una sola función se mantiene caliente) y se comparte mucha lógica; el costo es que todas las rutas terminan con los permisos más amplios y un código más grande.

---

## Reto adicional

_(Opcional: describir aquí el reto que se resuelva, por ejemplo filtro por estado, paginación o `DynamoDBWritePolicy`. Si no se hizo ninguno, eliminar esta sección.)_

## Checklist de entrega

- [x] `template.yaml`, `src/` y `samconfig.toml`
- [ ] Captura de los Outputs de `sam deploy`
- [ ] Capturas de las 5 operaciones CRUD
- [ ] Capturas de los errores 400 y 404
- [ ] Captura de los logs de CloudWatch
- [ ] Captura de `sam delete` completado
