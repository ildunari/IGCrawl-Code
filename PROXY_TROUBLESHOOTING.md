# BrightData Proxy Authentication Troubleshooting Guide

## Current Issue

Getting "407 Auth failed" error when trying to use BrightData proxy with Instagram scraping.

## Error Details

```
x-brd-err-code: client_10000
x-brd-err-msg: Invalid authentication: check credentials and retry. Bright Data credentials include your account ID, zone name and password
```

## BrightData Credential Format

According to the error message, BrightData credentials must include:
1. **Account ID** (customer ID)
2. **Zone name**
3. **Password**

The format is:
```
brd-customer-hl_CUSTOMER_ID-zone-ZONE_NAME:PASSWORD
```

## Current Configuration

```env
PROXY_USERNAME=brd-customer-hl_8d3663f1-zone-ig_crawl_center
PROXY_PASSWORD=9lvvluxub033
PROXY_HOST=brd.superproxy.io
PROXY_PORT=33335
```

## What to Check

1. **Verify Account ID**: The `8d3663f1` portion should be your actual BrightData customer/account ID
2. **Verify Zone Name**: The `ig_crawl_center` should be a valid zone name in your BrightData account
3. **Verify Password**: The `9lvvluxub033` should be the correct password for this zone
4. **Check Port**: Must use port 33335 with the new SSL certificate (not 22225)

## Steps to Fix

### 1. Log into BrightData Dashboard

1. Go to https://brightdata.com
2. Log into your account
3. Navigate to the proxy zones section

### 2. Find Correct Credentials

1. Look for your Instagram crawling zone
2. Note the exact zone name
3. Get the correct password for this zone
4. Confirm your customer ID

### 3. Update Configuration

Update the `.env` file with the correct values:
```env
PROXY_USERNAME=brd-customer-hl_YOUR_CUSTOMER_ID-zone-YOUR_ZONE_NAME
PROXY_PASSWORD=YOUR_ZONE_PASSWORD
```

### 4. SSL Certificate Configuration

For port 33335, you must use the new SSL certificate. The application should:
1. Load the certificate from the path
2. Use it for HTTPS connections
3. Or temporarily disable SSL verification during testing

## Testing the Proxy

Test directly with curl:
```bash
curl -v --proxy http://YOUR_USERNAME:YOUR_PASSWORD@brd.superproxy.io:33335 https://httpbin.org/ip
```

If using the certificate:
```bash
curl -v --proxy http://YOUR_USERNAME:YOUR_PASSWORD@brd.superproxy.io:33335 \
     --cacert "path/to/BrightData SSL certificate (port 33335).crt" \
     https://httpbin.org/ip
```

## Alternative Solutions

1. **Contact BrightData Support**
   - They can verify your credentials
   - Confirm the zone configuration
   - Check if the zone is active

2. **Create a New Zone**
   - Create a fresh zone specifically for Instagram
   - Use residential IPs
   - Get new credentials

3. **Use Different Proxy Service**
   - Consider alternatives like Oxylabs, SmartProxy
   - May have simpler authentication

## Code Implementation Notes

### HTTPX (GraphQL Scraper)
```python
client_args["proxies"] = {
    "http://": proxy_url,
    "https://": proxy_url
}
client_args["verify"] = False  # Or path to certificate
```

### Instagrapi (Instagram Scraper)
```python
self.private_client.set_proxy(proxy_url)
```

## Next Steps

1. Verify your BrightData account credentials
2. Update the `.env` file with correct values
3. Test with curl first
4. Restart the application
5. Monitor the logs for authentication errors

If the issue persists after verifying credentials, contact BrightData support with:
- Your customer ID
- Zone name
- The exact error message
- Timestamp of the failed request