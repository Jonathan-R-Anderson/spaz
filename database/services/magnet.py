from models import MagnetURL
from extensions import db
from system.logging import setup_logger

logger = setup_logger(__name__)

def _clear_magnet_urls(eth_address):
    logger.info(f"[clear_magnet_urls] Attempting to clear magnet URLs for eth_address={eth_address}")
    try:
        deleted_count = MagnetURL.query.filter_by(eth_address=eth_address).delete()
        db.session.commit()
        logger.info(f"[clear_magnet_urls] Successfully cleared {deleted_count} magnet URLs for {eth_address}")
        return {"message": f"All magnet URLs for {eth_address} have been cleared."}, 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[clear_magnet_urls] Failed to clear magnet URLs for {eth_address}: {e}")
        return {"error": f"Failed to clear magnet URLs: {str(e)}"}, 500


def _store_magnet_url(eth_address, magnet_url, snapshot_index):
    logger.info(f"[store_magnet_url] Storing magnet URL for eth_address={eth_address}, snapshot_index={snapshot_index}")
    try:
        new_magnet_url = MagnetURL(
            eth_address=eth_address,
            magnet_url=magnet_url,
            snapshot_index=snapshot_index
        )
        db.session.add(new_magnet_url)
        db.session.commit()
        logger.info(f"[store_magnet_url] Magnet URL stored for {eth_address}: {magnet_url}")
        return {"message": "Magnet URL stored successfully"}, 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[store_magnet_url] Failed to store magnet URL for {eth_address}: {e}")
        return {"error": f"Failed to store magnet URL: {str(e)}"}, 500
