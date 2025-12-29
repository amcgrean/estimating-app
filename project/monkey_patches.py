# project/monkey_patches.py
import hmac

def safe_str_cmp(a, b):
    return hmac.compare_digest(a, b)

# Attempt to patch flask_login.utils
try:
    import flask_login.utils
    flask_login.utils.safe_str_cmp = safe_str_cmp
except ImportError as e:
    print(f"Error importing flask_login.utils: {e}")

import logging
logging.basicConfig(level=logging.INFO)
logging.info('Applied monkey patch for safe_str_cmp in flask_login')
