import hashlib
import hmac
import random
import requests
import string
from shared import (
    User, MagnetURL, db, HMAC_SECRET_KEY, logging, app, blueprint
)

app.register_blueprint(blueprint)


# Function to clear all magnet URLs associated with an eth_address
def _clear_magnet_urls(eth_address):
    try:
        # Query to delete all entries related to the eth_address
        MagnetURL.query.filter_by(eth_address=eth_address).delete()
        db.session.commit()
        return {"message": f"All magnet URLs for {eth_address} have been cleared."}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to clear magnet URLs: {str(e)}"}, 500

# Generate a random secret for RTMP stream
def _generate_secret():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Hash the secret using HMAC with SHA-256
def _hash_secret(secret):
    return hmac.new(HMAC_SECRET_KEY.encode(), secret.encode(), hashlib.sha256).hexdigest()

# Store the secret in PostgreSQL
def _store_secret(eth_address, secret, ip_address):
    new_user = User(
        eth_address=eth_address,
        rtmp_secret=secret,
        ip_address=ip_address
    )
    db.session.add(new_user)
    db.session.commit()


# Store a magnet URL associated with the eth_address
def _store_magnet_url(eth_address, magnet_url, snapshot_index):
    new_magnet_url = MagnetURL(eth_address=eth_address, magnet_url=magnet_url, snapshot_index=snapshot_index)
    db.session.add(new_magnet_url)
    db.session.commit()
    return {"message": "Magnet URL stored successfully"}, 200

def _fetch_secret_from_api(eth_address):
    try:
        response = requests.get(f"http://localhost:5003/get_secret/{eth_address}", timeout=5)
        if response.status_code == 200:
            secret = response.json().get('secret')
            return secret
        else:
            logging.warning(f"[fetch_secret_from_api] Failed to get secret for {eth_address}: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"[fetch_secret_from_api] Exception fetching secret for {eth_address}: {e}")
        return None




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003, debug=True)
