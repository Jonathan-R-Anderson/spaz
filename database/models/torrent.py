from extensions import db
from datetime import datetime

class TorrentGroup(db.Model):
    __tablename__ = 'torrent_groups'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    files = db.relationship('TorrentFile', backref='group', lazy=True)


class TorrentFile(db.Model):
    __tablename__ = 'torrent_files'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('torrent_groups.id'), nullable=False)
    file_path = db.Column(db.Text, nullable=False)
    file_hash = db.Column(db.Text, nullable=False)
    magnet_url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
