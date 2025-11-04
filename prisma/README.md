# Prisma Setup

This directory contains the Prisma schema definition for the Social Video Processor.

## Initial Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Generate Prisma Client:

```bash
prisma generate
```

3. Push schema to database (development):

```bash
prisma db push
```

## Migrations

For production, use migrations instead of `db push`:

```bash
# Create a new migration
prisma migrate dev --name migration_name

# Apply migrations in production
prisma migrate deploy
```

## Database GUI

Open Prisma Studio to view and edit data:

```bash
prisma studio
```

## Usage in Code

```python
from prisma import Prisma
from utils.db import get_db, connect_db, disconnect_db

# At application startup
await connect_db()

# In your code
db = get_db()

# Create a user
user = await db.user.create(
    data={
        'oauthId': 'oauth_123',
        'notionAccessToken': 'token_abc'
    }
)

# Find a user
user = await db.user.find_unique(
    where={'oauthId': 'oauth_123'}
)

# Update a user
user = await db.user.update(
    where={'id': 1},
    data={'notionAccessToken': 'new_token'}
)

# Query with relations
user = await db.user.find_unique(
    where={'id': 1},
    include={'notionSchemas': True}
)

# At application shutdown
await disconnect_db()
```

## Schema Changes

After modifying `schema.prisma`:

1. Regenerate the client:

```bash
prisma generate
```

2. Push changes to database:

```bash
prisma db push  # Development
# OR
prisma migrate dev --name describe_changes  # Production-ready migration
```
