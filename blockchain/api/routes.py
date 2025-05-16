from flask import Blueprint

from api.views.update_site import update_site_routes
from api.views.retrieve_contract import retrieve_contract_routes
from api.views.magnets import magnets_routes
from api.views.config import config_routes
from api.views.register_contracts import register_contracts_routes

blueprint = Blueprint("web3_api", __name__)
blueprint.register_blueprint(update_site_routes)
blueprint.register_blueprint(retrieve_contract_routes)
blueprint.register_blueprint(magnets_routes)
blueprint.register_blueprint(config_routes)
blueprint.register_blueprint(register_contracts_routes)
