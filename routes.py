from flask import Blueprint
from api import api
from reset_admin_password import reset_admin_password

routes = Blueprint('routes', __name__)
routes.register_blueprint(api)
routes.register_blueprint(reset_admin_password)