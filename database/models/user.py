from extensions import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eth_address = db.Column(db.String(42), unique=True, nullable=False)
    rtmp_secret = db.Column(db.String(64), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)

    def __init__(self, eth_address, rtmp_secret, ip_address):
        self.eth_address = eth_address
        self.rtmp_secret = rtmp_secret
        self.ip_address = ip_address