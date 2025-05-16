from flask import Blueprint
from api.views.update_site import update_site_routes
from api.views.retrieve_contract import retrieve_contract_routes

blueprint = Blueprint("web3_api", __name__)

# Register subroutes
blueprint.register_blueprint(update_site_routes)
blueprint.register_blueprint(retrieve_contract_routes)
