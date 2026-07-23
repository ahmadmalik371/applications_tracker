import asyncio
import asyncpg
import os

async def main():
    url = os.environ.get('DATABASE_URL', 'postgresql://ats_user:13851098@localhost:5433/ats_db')
    print('Testing DB URL:', url)
    try:
        conn = await asyncpg.connect(url)
        print('Connected OK')
        await conn.close()
    except Exception as e:
        print('Connection error:', repr(e))

if __name__ == '__main__':
    asyncio.run(main())
