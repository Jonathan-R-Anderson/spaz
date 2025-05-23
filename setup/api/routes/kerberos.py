from flask import jsonify
from services.kerberos import write_conf, init_kdc, create_principal
from . import blueprint


@blueprint.route('/kerberos/write_conf', methods=['POST'])
def write_krb5_conf_route():
    return jsonify(write_conf())

@blueprint.route('/kerberos/init_kdc', methods=['POST'])
def init_kdc_route():
    return jsonify(init_kdc())

@blueprint.route('/kerberos/create_principal', methods=['POST'])
def create_principal_route():
    return jsonify(create_principal())
