from flask import Blueprint, jsonify
from services.kerberos import write_conf, init_kdc, create_principal

kerberos_bp = Blueprint("kerberos", __name__)

@kerberos_bp.route('/kerberos/write_conf', methods=['POST'])
def write_krb5_conf_route():
    return jsonify(write_conf())

@kerberos_bp.route('/kerberos/init_kdc', methods=['POST'])
def init_kdc_route():
    return jsonify(init_kdc())

@kerberos_bp.route('/kerberos/create_principal', methods=['POST'])
def create_principal_route():
    return jsonify(create_principal())
