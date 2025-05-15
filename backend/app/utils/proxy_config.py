"""
Proxy configuration utilities for BrightData integration
"""
import os
import ssl
import random
import tempfile
from typing import Optional, Dict
from pathlib import Path
from ..config import get_settings
import logging
import httpx

logger = logging.getLogger(__name__)

def get_brightdata_certificate_path() -> Optional[str]:
    """
    Get the path to BrightData SSL certificate specifically for port 33335.
    Checks multiple possible locations.
    """
    settings = get_settings()
    
    # Check configured path first (handle both absolute and relative paths)
    if settings.proxy_ssl_cert_path:
        if os.path.exists(settings.proxy_ssl_cert_path):
            return settings.proxy_ssl_cert_path
        # Try relative to project root
        project_root = Path(__file__).parent.parent.parent.parent
        cert_path = project_root / settings.proxy_ssl_cert_path
        if cert_path.exists():
            return str(cert_path)
    
    # Check common locations - prioritize the correct certificate for port 33335
    possible_paths = [
        # Check the exact path we configured in .env first
        "../ssl/brightdata_proxy_ca/BrightData SSL certificate (port 33335).crt",
        # Actual certificate location from our filesystem (with correct relative paths)
        "../ssl/brightdata_cert_bundle/brightdata_proxy_ca 2/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt",
        "../ssl/brightdata_proxy_ca/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt",
        "../ssl/brightdata_cert_bundle/brightdata_proxy_ca/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt",
        "../ssl/brightdata_proxy_ca 2/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt",
        "../ssl/brightdata_cert_bundle/ca.crt",
        "../ssl/brightdata_cert_bundle/brightdata.crt",
        "../ssl/brightdata_cert_bundle/ca-bundle.crt",
        # Also check absolute paths
        "/Users/kosta/Documents/ProjectsCode/IGCrawl-Code/ssl/brightdata_proxy_ca/BrightData SSL certificate (port 33335).crt",
        "/Users/kosta/Documents/ProjectsCode/IGCrawl-Code/ssl/brightdata_cert_bundle/brightdata_proxy_ca 2/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found BrightData certificate at: {path}")
            return path
    
    logger.warning("No BrightData certificate found in expected locations")
    return None

def create_session_id() -> str:
    """
    Create a unique session ID for consistent IP allocation
    """
    return f"{random.random():.10f}".replace(".", "")

def get_proxy_url(with_session=True) -> str:
    """
    Generate proxy URL with optional session ID
    """
    settings = get_settings()
    
    # Create username with session ID for sticky sessions
    username = settings.proxy_username
    if with_session:
        session_id = create_session_id()
        # Format: brd-customer-<customer_id>-zone-<zone_name>-session-<session_id>
        username = f"{username}-session-{session_id}"
    
    # Return properly formatted proxy URL
    return f"http://{username}:{settings.proxy_password}@{settings.proxy_host}:{settings.proxy_port}"

def create_ssl_context() -> ssl.SSLContext:
    """
    Create SSL context with BrightData certificate
    """
    ssl_context = ssl.create_default_context()
    cert_path = get_brightdata_certificate_path()
    
    if cert_path:
        try:
            ssl_context.load_verify_locations(cafile=cert_path)
            logger.info(f"Loaded BrightData certificate from: {cert_path}")
        except Exception as e:
            logger.error(f"Failed to load certificate: {e}")
            # Fall back to default certificates
            ssl_context = ssl.create_default_context()
    
    return ssl_context

def test_proxy_connection() -> bool:
    """
    Test if proxy connection is working
    """
    settings = get_settings()
    if not settings.use_proxy:
        return True
    
    proxy_url = get_proxy_url(with_session=True)
    ssl_context = create_ssl_context()
    
    try:
        # Test with httpx client - note that httpx uses 'proxy' not 'proxies'
        # Temporarily disable SSL verification for BrightData proxy
        client = httpx.Client(
            proxy=proxy_url,
            verify=False
        )
        
        response = client.get('https://lumtest.com/myip.json', timeout=10)
        result = response.json()
        logger.info(f"Proxy test successful: {result}")
        return True
    except Exception as e:
        logger.error(f"Proxy test failed: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def get_proxy_config(with_session=True) -> Dict[str, any]:
    """
    Get proxy configuration for HTTP clients with SSL support
    """
    settings = get_settings()
    
    if not settings.use_proxy:
        return {}
    
    proxy_url = get_proxy_url(with_session=with_session)
    ssl_context = create_ssl_context()
    
    config = {
        "proxies": {
            "http://": proxy_url,
            "https://": proxy_url
        },
        "verify": ssl_context
    }
    
    # Log proxy configuration (without password)
    safe_url = proxy_url.replace(settings.proxy_password, "****")
    logger.debug(f"Proxy configuration: {safe_url}")
    
    return config

def configure_httpx_client(client: httpx.Client, with_session=True) -> None:
    """
    Configure httpx client with proxy and SSL settings
    """
    settings = get_settings()
    
    if not settings.use_proxy:
        return
    
    proxy_url = get_proxy_url(with_session=with_session)
    cert_path = get_brightdata_certificate_path()
    
    # httpx uses proxy (singular) for all protocols
    client._proxy = proxy_url
    # Temporarily disable SSL verification for BrightData proxy
    client._verify = False

def configure_instagrapi_proxy(client, with_session=True) -> None:
    """
    Configure proxy for instagrapi client with SSL support
    """
    settings = get_settings()
    
    if not settings.use_proxy:
        return
    
    proxy_url = get_proxy_url(with_session=with_session)
    client.set_proxy(proxy_url)
    
    # Temporarily disable SSL verification for BrightData proxy issues
    try:
        # For the private API client sessions
        if hasattr(client, 'private') and hasattr(client.private, 'session'):
            client.private.session.verify = False
        # For the public API client sessions
        if hasattr(client, 'public'):
            client.public.verify = False
        # Try setting the requests adapter verify to False
        if hasattr(client, 'request_session'):
            client.request_session.verify = False
            
        logger.info(f"Configured instagrapi with proxy (SSL verification disabled)")
    except Exception as e:
        logger.error(f"Could not configure proxy for instagrapi: {e}")

def create_combined_certificate_bundle() -> Optional[str]:
    """
    Create a combined certificate bundle if multiple certificates exist
    """
    cert_files = []
    
    # List of certificate files to combine
    cert_paths = [
        get_brightdata_certificate_path(),  # Primary certificate
        "ssl/brightdata_cert_bundle/ca.crt",
        "ssl/brightdata_cert_bundle/intermediate.crt",
        "ssl/brightdata_cert_bundle/root.crt",
    ]
    
    for path in cert_paths:
        if path and os.path.exists(path):
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