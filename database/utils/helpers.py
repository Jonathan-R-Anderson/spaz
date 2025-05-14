import random
import ipaddress
from system.logging import setup_logger

logger = setup_logger(__name__)


def _gen_poster_id():
    try:
        poster_id = '%04X' % random.randint(0, 0xFFFF)
        logger.info(f"[gen_poster_id] Generated poster ID: {poster_id}")
        return poster_id
    except Exception as e:
        logger.error(f"[gen_poster_id] Failed to generate poster ID: {e}")
        raise


def _ip_to_int(ip_str):
    logger.info(f"[ip_to_int] Converting IP address to int: {ip_str}")
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        ip_bytes = ip_obj.packed
        ip_int = int.from_bytes(ip_bytes, byteorder="little") << 8
        logger.debug(f"[ip_to_int] IP bytes: {list(ip_bytes)}, Integer (shifted): {ip_int}")
        return ip_int
    except ValueError as e:
        logger.error(f"[ip_to_int] Invalid IP address format: {ip_str} | Error: {e}")
        raise
    except Exception as e:
        logger.error(f"[ip_to_int] Unexpected error converting IP address: {e}")
        raise
