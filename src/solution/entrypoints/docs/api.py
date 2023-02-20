from flask import Blueprint
from flask_restx import Api
from src.solution.entrypoints.docs.namespace import namespace

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(
    blueprint,
    version="1.0",
    title="Task Manager",
    description="-"
)

api.add_namespace(namespace)
