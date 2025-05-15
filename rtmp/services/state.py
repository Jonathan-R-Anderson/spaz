# services/state.py
from threading import Lock

# Runtime locks and shared state
magnet_url_lock = Lock()
is_monitoring_static = {}
is_monitoring_hls = {}
seeded_files = {}
snapshot_indices = {}
