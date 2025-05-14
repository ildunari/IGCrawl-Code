"""
Proxy configuration utilities for BrightData integration
"""
import os
import tempfile
from typing import Optional, Dict
from pathlib import Path
from ..config import get_settings

def get_brightdata_certificate_path() -> Optional[str]:
    """
    Get the path to BrightData SSL certificate.
    Checks multiple possible locations.
    """
    settings = get_settings()
    
    # Check configured path first
    if settings.proxy_ssl_cert_path and os.path.exists(settings.proxy_ssl_cert_path):
        return settings.proxy_ssl_cert_path
    
    # Check common locations
    possible_paths = [
        "ssl/brightdata_cert_bundle/ca.crt",
        "ssl/brightdata_cert_bundle/brightdata.crt",
        "ssl/brightdata_cert_bundle/ca-bundle.crt",
        "ssl/brightdata_cert_bundle/brightdata_proxy_ca 2/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt",
        "ssl/brightdata_proxy_ca/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def get_proxy_config() -> Dict[str, any]:
    """
    Get proxy configuration for HTTP clients
    """
    settings = get_settings()
    
    if not settings.use_proxy:
        return {}
    
    proxy_url = f"http://{settings.proxy_username}:{settings.proxy_password}@{settings.proxy_host}:{settings.proxy_port}"
    
    config = {
        "proxies": {
            "http://": proxy_url,
            "https://": proxy_url
        }
    }
    
    # Add certificate if available
    cert_path = get_brightdata_certificate_path()
    if cert_path:
        config["verify"] = cert_path
    else:
        # Use system certificates
        config["verify"] = True
    
    return config

def configure_instagrapi_proxy(client) -> None:
    """
    Configure proxy for instagrapi client
    """
    settings = get_settings()
    
    if not settings.use_proxy:
        return
    
    proxy_url = f"http://{settings.proxy_username}:{settings.proxy_password}@{settings.proxy_host}:{settings.proxy_port}"
    client.set_proxy(proxy_url)
    
    # Instagrapi might need certificate configuration differently
    cert_path = get_brightdata_certificate_path()
    if cert_path:
        # Some versions of instagrapi support setting certificates
        try:
            if hasattr(client, 'request_options'):
                client.request_options['verify'] = cert_path
            elif hasattr(client, 'http'):
                client.http.verify = cert_path
        except Exception as e:
            print(f"Could not set certificate for instagrapi: {e}")

def create_combined_certificate_bundle() -> Optional[str]:
    """
    Create a combined certificate bundle if multiple certificates exist
    """
    cert_files = []
    
    # List of certificate files to combine
    cert_paths = [
        "ssl/brightdata_cert_bundle/ca.crt",
        "ssl/brightdata_cert_bundle/intermediate.crt",
        "ssl/brightdata_cert_bundle/root.crt",
    ]
    
    for path in cert_paths:
        if os.path.exists(path):
            cert_files.append(path)
    
    if not cert_files:
        return None
    
    # Create temporary bundle file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bundle.crt', delete=False) as bundle:
        for cert_file in cert_files:
            with open(cert_file, 'r') as f:
                bundle.write(f.read())
                bundle.write('\n')
        
        return bundle.name