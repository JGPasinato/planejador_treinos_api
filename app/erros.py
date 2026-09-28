from fastapi.responses import JSONResponse

MENSAGENS = {
    "missing": "campo obrigatório",
    "literal_error": "valor inválido, use: {expected}",
    "string_too_short": "deve ter pelo menos {min_length} caracteres",
    "string_too_long": "deve ter no máximo {max_length} caracteres",
    "greater_than_equal": "deve ser maior ou igual a {ge}",
    "less_than_equal": "deve ser menor ou igual a {le}",
    "int_parsing": "deve ser um número inteiro",
    "float_parsing": "deve ser um número",
    "datetime_parsing": "data e hora inválidas, use o formato 2026-09-25T06:00:00",
    "datetime_from_date_parsing": "data e hora inválidas, use o formato 2026-09-25T06:00:00",
    "json_invalid": "JSON inválido",
}


def erro_validacao(request, exc):
    erros = []
    for erro in exc.errors():
        campo = ".".join(str(p) for p in erro["loc"] if p not in ("body", "query", "path"))
        ctx = erro.get("ctx", {})
        if "expected" in ctx:
            ctx["expected"] = ctx["expected"].replace("'", "").replace(" or ", ", ")
        try:
            mensagem = MENSAGENS[erro["type"]].format(**ctx)
        except KeyError:
            mensagem = "valor inválido"
        erros.append(f"{campo}: {mensagem}" if campo else mensagem)
    return JSONResponse(status_code=422, content={"detail": "; ".join(erros)})
