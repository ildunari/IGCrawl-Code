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
        # Check the simplified path first (recommended)
        "../ssl/brightdata/brightdata.crt",
        "/Users/kosta/Documents/ProjectsCode/IGCrawl-Code/ssl/brightdata/brightdata.crt",
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
    
    # Create a combined certificate bundle for better compatibility
    bundle_path = create_combined_certificate_bundle()
    
    try:
        # Get certificate path
        cert_path = bundle_path if bundle_path else get_brightdata_certificate_path()
        logger.info(f"Testing proxy connection using certificate: {cert_path}")
        
        # Test with httpx client using the certificate if available
        client = httpx.Client(
            proxy=proxy_url,
            verify=cert_path if cert_path else False
        )
        
        response = client.get('https://lumtest.com/myip.json', timeout=10)
        result = response.json()
        logger.info(f"Proxy test successful: {result}")
        return True
    except Exception as e:
        logger.error(f"Proxy test failed: {str(e)}")
        logger.warning("Falling back to disabled SSL verification for testing")
        try:
            # Try again with SSL verification disabled
            client = httpx.Client(
                proxy=proxy_url,
                verify=False
            )
            response = client.get('https://lumtest.com/myip.json', timeout=10)
            result = response.json()
            logger.warning(f"Proxy test with disabled SSL verification successful: {result}")
            return True
        except Exception as fallback_e:
            logger.error(f"Proxy fallback test also failed: {str(fallback_e)}")
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
    
    # Create a combined certificate bundle for better compatibility
    bundle_path = create_combined_certificate_bundle()
    
    # If we have a bundle, use it; otherwise, use the primary certificate
    if bundle_path:
        verify = bundle_path
        logger.info(f"Using combined certificate bundle: {bundle_path}")
    else:
        cert_path = get_brightdata_certificate_path()
        verify = cert_path if cert_path else False
        logger.info(f"Using single certificate: {cert_path}")
    
    config = {
        "proxies": {
            "http://": proxy_url,
            "https://": proxy_url
        },
        "verify": verify
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
    
    # Create a combined certificate bundle for better compatibility
    bundle_path = create_combined_certificate_bundle()
    
    # If we have a bundle, use it; otherwise, use the primary certificate
    if bundle_path:
        verify = bundle_path
        logger.info(f"Configuring httpx client with certificate bundle: {bundle_path}")
    else:
        cert_path = get_brightdata_certificate_path()
        verify = cert_path if cert_path else False
        logger.info(f"Configuring httpx client with certificate: {cert_path}")
    
    # httpx uses proxy (singular) for all protocols
    client._proxy = proxy_url
    client._verify = verify
    
    # If verify is False, log a warning
    if not verify:
        logger.warning("SSL verification disabled for httpx client - this is insecure!")

def configure_instagrapi_proxy(client, with_session=True) -> None:
    """
    Configure proxy for instagrapi client with SSL support
    """
    settings = get_settings()
    
    if not settings.use_proxy:
        return
    
    proxy_url = get_proxy_url(with_session=with_session)
    client.set_proxy(proxy_url)
    
    # Create a combined certificate bundle for better compatibility
    bundle_path = create_combined_certificate_bundle()
    
    # Try to configure the client with our certificate bundle
    try:
        # First try with certificate bundle
        if bundle_path:
            logger.info(f"Configuring instagrapi with certificate bundle: {bundle_path}")
            # For the private API client sessions
            if hasattr(client, 'private') and hasattr(client.private, 'session'):
                client.private.session.verify = bundle_path
            # For the public API client sessions
            if hasattr(client, 'public'):
                client.public.verify = bundle_path
            # Try setting the requests adapter verify
            if hasattr(client, 'request_session'):
                client.request_session.verify = bundle_path
        else:
            # Try with single certificate
            cert_path = get_brightdata_certificate_path()
            if cert_path:
                logger.info(f"Configuring instagrapi with certificate: {cert_path}")
                # For the private API client sessions
                if hasattr(client, 'private') and hasattr(client.private, 'session'):
                    client.private.session.verify = cert_path
                # For the public API client sessions
                if hasattr(client, 'public'):
                    client.public.verify = cert_path
                # Try setting the requests adapter verify
                if hasattr(client, 'request_session'):
                    client.request_session.verify = cert_path
            else:
                # Fall back to disabled SSL verification if no certificate is available
                logger.warning("DISABLING SSL VERIFICATION FOR INSTAGRAPI - USING PROXY WITHOUT CERTIFICATE VERIFICATION!")
                if hasattr(client, 'private') and hasattr(client.private, 'session'):
                    client.private.session.verify = False
                if hasattr(client, 'public'):
                    client.public.verify = False
                if hasattr(client, 'request_session'):
                    client.request_session.verify = False
                
        logger.info(f"Configured instagrapi with proxy and SSL settings")
    except Exception as e:
        logger.error(f"Could not configure proxy for instagrapi: {e}")
        logger.warning("DISABLING SSL VERIFICATION FOR INSTAGRAPI - USING PROXY WITHOUT CERTIFICATE VERIFICATION!")
        # Fall back to disabled SSL verification
        try:
            if hasattr(client, 'private') and hasattr(client.private, 'session'):
                client.private.session.verify = False
            if hasattr(client, 'public'):
                client.public.verify = False
            if hasattr(client, 'request_session'):
                client.request_session.verify = False
        except Exception as fallback_e:
            logger.error(f"Could not even configure fallback settings: {fallback_e}")

def create_combined_certificate_bundle() -> Optional[str]:
    """
    Create a combined certificate bundle if multiple certificates exist
    """
    logger.info("Creating combined certificate bundle...")
    cert_files = []
    
    # Main certificate paths to try
    main_cert_path = get_brightdata_certificate_path()
    if main_cert_path:
        cert_files.append(main_cert_path)
        logger.info(f"Added primary certificate: {main_cert_path}")
    
    # List of additional certificate files to combine
    project_root = Path(__file__).parent.parent.parent.parent
    additional_cert_paths = [
        project_root / "ssl/brightdata_cert_bundle/ca.crt",
        project_root / "ssl/brightdata_cert_bundle/intermediate.crt",
        project_root / "ssl/brightdata_cert_bundle/root.crt",
        # Also check system certificate store paths
        "/etc/ssl/certs/ca-certificates.crt",  # Debian/Ubuntu
        "/etc/pki/tls/certs/ca-bundle.crt",    # CentOS/RHEL
        "/etc/ssl/ca-bundle.pem",              # OpenSUSE
        "/usr/local/share/certs/ca-root-nss.crt", # FreeBSD
        "/usr/local/etc/openssl/cert.pem",     # macOS
    ]
    
    # Add any valid certificate files
    for path in additional_cert_paths:
        if os.path.exists(str(path)):
            cert_files.append(str(path))
            logger.info(f"Added additional certificate: {path}")
    
    if not cert_files:
        logger.warning("No certificate files found for bundle")
        return None
    
    # Create temporary bundle file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bundle.crt', delete=False) as bundle:
        bundle_path = bundle.name
        for cert_file in cert_files:
            try:
                with open(cert_file, 'r') as f:
                    bundle.write(f.read())
                    bundle.write('\n')
            except Exception as e:
                logger.error(f"Error reading certificate file {cert_file}: {e}")
        
        logger.info(f"Created certificate bundle at: {bundle_path}")
        return bundle_path