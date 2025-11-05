# Prisma Migration Guide

This project has been migrated from raw SQL/psycopg2 to Prisma ORM.

## What Changed

### Before (SQL/psycopg2)

- Raw SQL migrations in `migrations/` directory
- Manual connection pooling in `models/database.py`
- Custom model classes with manual SQL queries
- Manual relationship management

### After (Prisma)

- Declarative schema in `prisma/schema.prisma`
- Automatic client generation with type safety
- Built-in connection management
- Automatic relationship handling
- Migration system built-in

## Key Benefits

1. **Type Safety**: Prisma Client Python provides full type hints
2. **Auto-completion**: IDE support for all database operations
3. **Migrations**: Built-in migration system with version control
4. **Relations**: Automatic handling of foreign keys and relations
5. **Query Builder**: Intuitive API for complex queries
6. **Prisma Studio**: Built-in database GUI

## Setup Instructions

1. **Install Prisma**:

```bash
pip install prisma
```

2. **Generate Client**:

```bash
prisma generate
```

3. **Push Schema to Database** (Development):

```bash
prisma db push
```

4. **Create Migration** (Production):

```bash
prisma migrate dev --name initial_schema
```

## Code Examples

### Creating Records

**Before (psycopg2)**:

```python
from models.database import get_db_cursor

with get_db_cursor() as cursor:
    cursor.execute(
        "INSERT INTO users (oauth_id, notion_access_token) VALUES (%s, %s) RETURNING id",
        (oauth_id, token)
    )
    user_id = cursor.fetchone()[0]
```

**After (Prisma)**:

```python
from utils.db import get_db

db = get_db()
user = await db.user.create(
    data={
        'oauthId': oauth_id,
        'notionAccessToken': token
    }
)
```

### Querying with Relations

**Before (psycopg2)**:

```python
# Multiple queries needed
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
user = cursor.fetchone()

cursor.execute("SELECT * FROM notion_schemas WHERE user_id = %s", (user_id,))
schemas = cursor.fetchall()
```

**After (Prisma)**:

```python
# Single query with automatic joins
user = await db.user.find_unique(
    where={'id': user_id},
    include={'notionSchemas': True}
)
```

### Updating Records

**Before (psycopg2)**:

```python
cursor.execute(
    "UPDATE users SET notion_access_token = %s WHERE id = %s",
    (new_token, user_id)
)
```

**After (Prisma)**:

```python
user = await db.user.update(
    where={'id': user_id},
    data={'notionAccessToken': new_token}
)
```

## Application Integration

### Flask App Initialization

```python
from flask import Flask
from utils.db import connect_db, disconnect_db

app = Flask(__name__)

@app.before_serving
async def startup():
    await connect_db()

@app.after_serving
async def shutdown():
    await disconnect_db()
```

### Using in Routes

```python
from flask import jsonify
from utils.db import get_db

@app.route('/users/<int:user_id>')
async def get_user(user_id):
    db = get_db()
    user = await db.user.find_unique(
        where={'id': user_id},
        include={
            'notionSchemas': True,
            'linkDatabases': True
        }
    )

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'oauthId': user.oauthId,
        'schemas': [s.tag for s in user.notionSchemas]
    })
```

## Common Operations

### Find One

```python
user = await db.user.find_unique(where={'oauthId': 'oauth_123'})
```

### Find Many

```python
schemas = await db.notionschema.find_many(
    where={'userId': user_id},
    order={'createdAt': 'desc'}
)
```

### Create with Relations

```python
user = await db.user.create(
    data={
        'oauthId': 'oauth_123',
        'notionAccessToken': 'token',
        'notionSchemas': {
            'create': [
                {'dbId': 'db1', 'tag': 'cooking', 'schema': {...}},
                {'dbId': 'db2', 'tag': 'places', 'schema': {...}}
            ]
        }
    }
)
```

### Update

```python
schema = await db.notionschema.update(
    where={'id': schema_id},
    data={'prompt': 'New prompt'}
)
```

### Delete

```python
await db.user.delete(where={'id': user_id})
# Related records cascade automatically
```

### Count

```python
count = await db.processingqueue.count(
    where={'status': 'queued'}
)
```

## Testing

Prisma works great with pytest:

```python
import pytest
from utils.db import get_db, connect_db, disconnect_db

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    await connect_db()
    yield
    await disconnect_db()

@pytest.mark.asyncio
async def test_create_user():
    db = get_db()
    user = await db.user.create(
        data={
            'oauthId': 'test_oauth',
            'notionAccessToken': 'test_token'
        }
    )
    assert user.oauthId == 'test_oauth'

    # Cleanup
    await db.user.delete(where={'id': user.id})
```

## Resources

- [Prisma Client Python Docs](https://prisma-client-py.readthedocs.io/)
- [Prisma Schema Reference](https://www.prisma.io/docs/reference/api-reference/prisma-schema-reference)
- [Prisma CLI Reference](https://www.prisma.io/docs/reference/api-reference/command-reference)
