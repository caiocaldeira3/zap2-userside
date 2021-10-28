from flask import Response

DeletedObject = Response(
    response={"msg": "Objeto deletado com sucesso do banco de dados"},
    status=204,
    mimetype="application/json"
)

NotModified = Response(
    response={"msg": "Objeto não modificado"},
    status=304,
    mimetype="application/json"
)

ServerError = Response(
    response={"error": "Houve um problema conectando com o servidor da API"},
    status=500,
    mimetype="application/json"
)

NotFoundError = Response(
    response={"error": "Não foi possível encontrar a página que você estava procurando"},
    status=404,
    mimetype="application/json"
)

AuthorizationError = Response(
    response={"error": "Você não tem acesso à essa página"},
    status=403,
    mimetype="application/json"
)

DuplicateError = Response(
    response={"error": "Objeto já cadastrado"},
    status=500,
    mimetype="application/json"
)
