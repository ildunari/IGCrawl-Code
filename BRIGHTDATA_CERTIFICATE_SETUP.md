# BrightData Certificate Bundle Setup Guide

## Downloading the Certificate Bundle

1. Log into your BrightData account
2. Navigate to your proxy zone settings
3. Look for "Load cert into code" option
4. Download the zip file

## Installing the Certificate

1. Extract the downloaded zip file
2. Copy the certificate files to:
   ```
   IGCrawl-Code/ssl/brightdata_cert_bundle/
   ```

3. The zip typically contains:
   - `ca.crt` - The Certificate Authority certificate
   - Additional certificates or bundle files
   - Sometimes code examples

## Expected File Structure

```
IGCrawl-Code/
├── ssl/
│   ├── brightdata_cert_bundle/
│   │   ├── ca.crt              # Main certificate
│   │   ├── intermediate.crt    # Optional intermediate cert
│   │   └── instructions.txt    # Optional instructions
│   └── brightdata_proxy_ca/    # Old certificate location
```

## Configuration

The application will automatically detect the certificate:

1. First checks the path in `.env`: `PROXY_SSL_CERT_PATH`
2. Then checks common locations:
   - `ssl/brightdata_cert_bundle/ca.crt`
   - `ssl/brightdata_cert_bundle/brightdata.crt`
   - `ssl/brightdata_cert_bundle/ca-bundle.crt`

## Testing the Certificate

After installing the certificate:

1. Enable proxy in `.env`:
   ```env
   USE_PROXY=true
   ```

2. Restart the services:
   ```bash
   docker compose restart backend worker
   ```

3. Check the logs for certificate loading:
   ```bash
   docker compose logs worker -f
   ```

   You should see:
   ```
   Using SSL certificate: ssl/brightdata_cert_bundle/ca.crt
   ```

## Troubleshooting

### Certificate Not Found
- Check file permissions
- Verify the file path
- Make sure Docker can access the volume

### SSL Verification Failed
- Try using the full certificate bundle
- Update the certificate path in `.env`
- Contact BrightData support for the correct certificate

### Still Getting 407 Errors
- This is an authentication issue, not certificate
- Verify your credentials are correct
- Check zone configuration in BrightData

## Code Implementation

The application handles certificates automatically through:
- `backend/app/utils/proxy_config.py` - Certificate detection
- `backend/app/scrapers/graphql_scraper.py` - HTTPX client
- `backend/app/scrapers/instagram_scraper.py` - Instagrapi client

No code changes needed after certificate installation!