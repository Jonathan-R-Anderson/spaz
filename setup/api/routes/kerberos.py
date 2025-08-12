"""Kerberos-related API routes."""

from flask import Blueprint, jsonify

from services.kerberos import create_principal, init_kdc, write_conf

# Each route module exposes its own blueprint so the application factory can
# register them individually. This module defines the blueprint expected by the
# application: ``kerberos_bp``.
kerberos_bp = Blueprint("kerberos", __name__)


@kerberos_bp.route("/kerberos/write_conf", methods=["POST"])
def write_krb5_conf_route():
    """Write the Kerberos configuration file."""
    return jsonify(write_conf())


@kerberos_bp.route("/kerberos/init_kdc", methods=["POST"])
def init_kdc_route():
    """Initialise the Kerberos KDC."""
    return jsonify(init_kdc())


@kerberos_bp.route("/kerberos/create_principal", methods=["POST"])
def create_principal_route():
    """Create a Kerberos principal."""
    return jsonify(create_principal())
