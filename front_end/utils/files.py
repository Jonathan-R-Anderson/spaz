
# Helper Functions
def _gen_poster_id():
    return '%04X' % random.randint(0, 0xffff)

def _ip_to_int(ip_str):
    return int.from_bytes(
        ipaddress.ip_address(ip_str).packed,
        byteorder="little"
    ) << 8

def _allowed_file(filename):
    """Check if the file has an allowed extension."""
    return True