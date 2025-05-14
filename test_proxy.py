
import os
import requests
import sys

# Proxy details from .env file
PROXY_HOST = "brd.superproxy.io"
PROXY_PORT = "33335"
PROXY_USERNAME = "brd-customer-hl_8d3663f1-zone-ig_crawl_center"
PROXY_PASSWORD = "9lvvluxub033"
CERT_PATH = os.path.join("ssl", "brightdata_cert_bundle", "brightdata_proxy_ca 2", 
                         "New SSL certifcate - MUST BE USED WITH PORT 33335", 
                         "BrightData SSL certificate (port 33335).crt")

# Build proxy URL
proxy_url = f"http://{PROXY_USERNAME