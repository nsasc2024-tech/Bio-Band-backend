# GitHub + Turso Integration Setup

## 1. Add Turso Secrets to GitHub

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `TURSO_AUTH_TOKEN`: Your Turso authentication token
- `TURSO_DB_URL`: libsql://bioband-praveencoder2007.aws-ap-south-1.turso.io
- `TURSO_DB_TOKEN`: Your database token

## 2. Get Turso Auth Token

```bash
turso auth token
```

## 3. Manual Sync Commands

```bash
# Install Turso CLI
curl -sSfL https://get.tur.so/install.sh | bash

# Authenticate
turso auth token YOUR_TOKEN_HERE

# Apply schemas
turso db shell bioband-praveencoder2007 < database/schemas/minimal_db.sql
turso db shell bioband-praveencoder2007 < database/schemas/chat_messages.sql
```

## 4. Automatic Deployment

The GitHub Action will automatically:
- Install Turso CLI
- Authenticate with your token
- Run database migrations on every push to main branch