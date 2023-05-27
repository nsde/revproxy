import random
import requests

import config

host_ip = requests.get('https://checkip.amazonaws.com', timeout=2).text.strip()

def random_ip():
    """Generates a random IP address."""
    return '.'.join([str(random.randint(0, 255)) for _ in range(4)])

def localhost():
    """Returns the localhost IP address."""
    return '127.0.0.1'

def apply_privacy(setting: str, actual_value: str):
    """Applies privacy settings to the given value."""

    setting = config.read()[setting]

    return {
        'expose': actual_value,
        'obfuscate': random_ip(),
        'localhost': localhost()
    }[setting]

