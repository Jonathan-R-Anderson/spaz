
def _clear_magnet_urls(eth_address):
    try:
        MagnetURL.query.filter_by(eth_address=eth_address).delete()
        db.session.commit()
        return {"message": f"All magnet URLs for {eth_address} have been cleared."}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to clear magnet URLs: {str(e)}"}, 500

def _store_magnet_url(eth_address, magnet_url, snapshot_index):
    new_magnet_url = MagnetURL(eth_address=eth_address, magnet_url=magnet_url, snapshot_index=snapshot_index)
    db.session.add(new_magnet_url)
    db.session.commit()
    return {"message": "Magnet URL stored successfully"}, 200