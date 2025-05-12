import random
import ipaddress

def gen_poster_id():
    return '%04X' % random.randint(0, 0xFFFF)

def ip_to_int(ip_str):
    return int.from_bytes(ipaddress.ip_address(ip_str).packed, byteorder="little") << 8
