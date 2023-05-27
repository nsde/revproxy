"""Module for blocking requests etc."""

from adblockparser import AdblockRules

with open('config/blocklist.txt', 'r', encoding='utf8') as ad_list_file:
    rules = AdblockRules(ad_list_file.read().splitlines())

def should_block(url: str) -> bool:
    """Returns whether the given URL should be blocked."""

    return rules.should_block(url)
