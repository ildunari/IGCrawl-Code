# BrightData Proxy Configuration Guide for Claude Desktop

## Context
You're helping to configure a BrightData proxy for an Instagram scraping application. The proxy is returning "407 Auth failed" errors, which means the authentication credentials are incorrect or the proxy zone is not properly configured.

## Current Proxy Credentials
- Username: `brd-customer-hl_8d3663f1-zone-ig_crawl_center`
- Password: `9lvvluxub033`
- Host: `brd.superproxy.io`
- Port: `33335`
- Certificate: Already installed at `/ssl/brightdata_cert_bundle/` (for port 33335)

## Error Message from BrightData
```
407 Authentication failed
Invalid authentication: check credentials and retry. 
Bright Data credentials include your account ID, zone name and password
```

## What Needs to Be Done

### 1. Login to BrightData
- Navigate to https://brightdata.com/cp/zones
- Login using Google OAuth (or your credentials)
- You should see the BrightData control panel

### 2. Verify/Create the Proxy Zone
Check if a zone named `ig_crawl_center` exists:
- Look for it in the zones list
- If it doesn't exist, you need to create it

### 3. Create Zone (if needed)
If the zone doesn't exist:
1. Click "Add Zone" or "Create Zone"
2. Name it exactly: `ig_crawl_center`
3. Select proxy type (preferably Residential Proxies)
4. Configure the zone settings:
   - Enable the zone
   - Set any IP rotation settings if available
   - Save the zone

### 4. Check Zone Credentials
Once the zone exists:
1. Click on the `ig_crawl_center` zone
2. Look for the credentials section
3. Verify:
   - Customer ID matches: `hl_8d3663f1`
   - Zone name is: `ig_crawl_center`
   - Note the password (it might be different from `9lvvluxub033`)

### 5. Verify Zone Status
Make sure the zone is:
- Active (not suspended or disabled)
- Has available proxy IPs
- Doesn't have any billing issues

### 6. Get the Correct Port
Check what port the zone is configured to use:
- It should be 33335 (for SSL with the new certificate)
- If it's different, note the correct port

### 7. Test the Proxy
In BrightData's control panel, there's usually a "Test" or "Try" button:
1. Click the test button for the zone
2. Try to make a request to a test URL
3. See if it succeeds

### 8. Collect the Correct Credentials
After verifying everything, provide the correct credentials:
- Full username (customer-ID-zone-name format)
- Correct password
- Correct port number
- Zone status (active/inactive)
- Any error messages you see

## Important Information to Look For
1. Is the zone `ig_crawl_center` active?
2. What's the exact username format shown in BrightData?
3. What's the actual password for the zone?
4. Are there any error messages or warnings on the zone?
5. Is the account in good standing (no billing issues)?
6. What port is configured for the zone?

## Screenshots to Take
1. The zones list page
2. The `ig_crawl_center` zone details (if it exists)
3. The credentials section
4. Any error messages or warnings
5. The test/try proxy section if available

## Common Issues to Check
- Zone might be suspended due to billing
- Zone might not exist and needs to be created
- Password might have been changed
- Port might be different than expected
- Certificate might not match the port

Please navigate through these steps and provide screenshots or information about what you find. This will help determine why the proxy authentication is failing.