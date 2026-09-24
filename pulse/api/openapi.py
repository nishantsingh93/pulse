from fastapi.openapi.utils import get_openapi


def convert(node):
    if isinstance(node, list):
        return [convert(value) for value in node]
    if not isinstance(node, dict):
        return node
    result = {key: convert(value) for key, value in node.items() if key != "jsonSchemaDialect"}
    if "const" in result:
        result["enum"] = [result.pop("const")]
    choices = result.get("anyOf")
    if isinstance(choices, list):
        non_null = [choice for choice in choices if choice != {"type": "null"}]
        if len(non_null) != len(choices):
            result.pop("anyOf")
            if len(non_null) == 1:
                choice = non_null[0]
                if "$ref" in choice:
                    result["allOf"] = [choice]
                else:
                    result.update(choice)
            else:
                result["anyOf"] = non_null
            result["nullable"] = True
    return result


def openapi_30(app):
    if app.openapi_schema:
        return app.openapi_schema
    raw = get_openapi(title=app.title, version=app.version, routes=app.routes)
    raw["openapi"] = "3.0.3"
    app.openapi_schema = convert(raw)
    return app.openapi_schema
