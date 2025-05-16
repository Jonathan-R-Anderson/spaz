import os
from flask import Blueprint, render_template, request

dynamic_bp = Blueprint("dynamic_bp", __name__)

@dynamic_bp.route('/', defaults={'path': ''})
@dynamic_bp.route('/<path:path>')
def catch_all(path):
    # Extract domain (e.g., from Host header or path)
    host = request.host.split(':')[0]  # drop port if present
    domain_path = os.path.join('static', 'sites', host)

    # Fallback to 404 if site isn't hosted
    if not os.path.exists(domain_path):
        return f"Site for {host} not found", 404

    # Serve the dynamic loader HTML shell
    return render_template("dynamic_page.html", domain=host, route=path)
