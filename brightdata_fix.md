# BrightData Proxy Configuration Fix

After analyzing your current BrightData setup, I've identified the issues causing the "407 Auth failed" errors. Here are the corrections needed:

## 1. Password Issue

There's a discrepancy in your password. In your `.env` file, it's set as:
```
PROXY_PASSWORD=9lvvluxub033
```

But in the BrightData dashboard, the actual password is:
```
PROXY_PASSWORD=9lvviuxub033
```

Note the difference: `9lvvluxub033` (with "lux") vs `9lvviuxub033` (with "viu").

## 2. SSL Certificate Path Issue

Your current SSL certificate path in the `.env` file is incorrect:
```
PROXY_SSL_CERT_PATH=ssl/brightdata_proxy_ca/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt
```

The actual path on your system appears to be:
```
ssl/brightdata_cert_bundle/brightdata_proxy_ca 2/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt
```

## 3. Updated .env File

Here's the corrected configuration for your `.env` file:

```
# Instagram credentials
INSTAGRAM_USERNAME=TransatlanticFrames
INSTAGRAM_PASSWORD=F3EH.NtT@twpcqc

# Proxy Configuration (BrightData)
USE_PROXY=true
PROXY_HOST=brd.superproxy.io
PROXY_PORT=33335
PROXY_USERNAME=brd-customer-hl_8d3663f1-zone-ig_crawl_center
PROXY_PASSWORD=9lvviuxub033
PROXY_SSL_CERT_PATH=ssl/brightdata_cert_bundle/brightdata_proxy_ca 2/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt

# Rate limiting (more relaxed for development)
RATE_LIMIT_PER_MINUTE=10
SCRAPE_DELAY_SECONDS=5
```

## 4. Alternative SSL Certificate Solution

If you continue to experience SSL certificate issues, BrightData provides a certificate bundle that you can download from your account:

1. Go to https://brightdata.com/static/brightdata_proxy_ca.zip
2. Extract the certificate file
3. Place it in your project's SSL directory
4. Update the path in your `.env` file

## 5. Testing the Setup

To test if your proxy is working correctly with the new settings, you can use this curl command:

```bash
curl -i --proxy brd.superproxy.io:33335 --proxy-user brd-customer-hl_8d3663f1-zone-ig_crawl_center:9lvviuxub033 --cacert "path/to/certificate.crt" "https://geo.brdtest.com/welcome.txt"
```

## 6. Alternative Approach

If you continue to experience issues, you can temporarily disable SSL verification in your application for testing purposes. In your backend code, look for where the HTTP client is initialized and add an option to disable SSL verification. Note that this is only recommended for testing, not for production use.

```python
# In Python with requests:
requests.get(url, proxies=proxy_dict, verify=False)

# In Python with httpx:
client = httpx.Client(proxies=proxy_url, verify=False)
```

Make these changes, restart your application, and you should be able to successfully connect to Instagram through the BrightData proxy.
