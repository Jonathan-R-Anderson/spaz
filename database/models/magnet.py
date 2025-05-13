from extensions import db

class MagnetURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eth_address = db.Column(db.String(42), nullable=False)
    magnet_url = db.Column(db.Text, nullable=False)
    snapshot_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
