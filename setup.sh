#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.template .env

# Generate secret keys and append to .env
python3 - <<'PY'
import base64, os

# Generate encryption keys
enc = base64.urlsafe_b64encode(os.urandom(32)).decode()
sec = base64.urlsafe_b64encode(os.urandom(32)).decode()
insta = base64.urlsafe_b64encode(os.urandom(32)).decode()

# Read existing .env
with open('.env', 'r') as f:
    content = f.read()

content = content.replace('SECRET_KEY=...', f'SECRET_KEY={sec}')
content = content.replace('ENCRYPTION_KEY=...', f'ENCRYPTION_KEY={enc}')
content = content.replace('INSTAGRAM_ENCRYPTION_KEY=...', f'INSTAGRAM_ENCRYPTION_KEY={insta}')

with open('.env', 'w') as f:
    f.write(content)

print('\u2705 Generated and configured secret keys')
PY

# Install npm dependencies if package.json exists
if [ -f "package.json" ]; then
    npm install
    echo "✅ Installed npm dependencies"
fi

# Make scripts executable
chmod +x scripts/*.sh scripts/*.ps1 2>/dev/null || true

# Create necessary directories
mkdir -p data logs ssl/brightdata_proxy_ca 2>/dev/null || true

# Run verification script if it exists
if [ -f "scripts/verify_installation.py" ]; then
    python scripts/verify_installation.py
    echo "✅ Environment verification completed"
fi

echo "🚀 Setup completed successfully!"
