# Helpers
from urllib.parse import urlparse, urljoin

def same_domain(base, target):
    return urlparse(base).netloc == urlparse(target).netloc

def normalize_url(base, link):
    return urljoin(base, link.split("#")[0])
