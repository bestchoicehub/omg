from flask import Blueprint

operation = Blueprint('operation', __name__)

from . import views, errors
from ..models.Permission import Permission

@operation.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)