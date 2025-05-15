import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_brightdata_instagram():
    """Test BrightData proxy with Instagram"""
    # Get proxy configuration
    proxy_host = os.getenv('PROXY_HOST', 'brd.superproxy.io')
    proxy_port = os.getenv('PROXY_PORT', '33335')
    proxy_username = os.getenv('PROXY_USERNAME')
    proxy_password = os.getenv('PROXY_PASSWORD')
    
    if not proxy_username or not proxy_password:
        print("❌ Missing proxy credentials in .env file")
        return
    
    # Create proxy URL
    proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    print(f"Testing BrightData proxy for Instagram...")
    print(f"Proxy: {proxy_host}:{proxy_port}")
    print(f"Username: {proxy_username}")
    
    # Test 1: Basic connectivity
    print("\n1. Testing basic proxy connectivity...")
    try:
        response = requests.get(
            'https://lumtest.com/myip.json',
            proxies=proxies,
            verify=False,
            timeout=30
        )
        result = response.json()
        print(f"   ✓ Connected via proxy")
        print(f"   IP: {result.get('ip', 'Unknown')}")
        print(f"   Country: {result.get('country', 'Unknown')}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return
    
    # Test 2: Instagram main page
    print("\n2. Testing Instagram main page...")
    try:
        response = requests.get(
            'https://www.instagram.com/',
            proxies=proxies,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            },
            verify=False,
            timeout=30
        )
        print(f"   Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Successfully accessed Instagram")
        else:
            print(f"   ✗ Failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 3: Instagram API endpoint
    print("\n3. Testing Instagram API endpoint...")
    try:
        response = requests.get(
            'https://www.instagram.com/api/v1/web/accounts/login/',
            proxies=proxies,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'X-Requested-With': 'XMLHttpRequest',
            },
            verify=False,
            timeout=30
        )
        print(f"   Status code: {response.status_code}")
        if response.status_code in [200, 400, 403]:
            print(f"   ✓ API endpoint reachable")
        else:
            print(f"   ✗ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    print("\n=== BrightData Configuration Recommendations ===")
    print("1. Ensure your zone is set to 'Residential' or 'Mobile' (not Datacenter)")
    print("2. Enable SSL decryption in your zone settings")
    print("3. Add instagram.com to your target sites")
    print("4. Use sticky sessions for consistent IPs")
    print("5. Consider using a different port (22225 vs 33335)")
    print("6. Check if your zone has Instagram-specific settings")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    test_brightdata_instagram()
