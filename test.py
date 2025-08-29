import asyncio, asyncpg

async def test():
    conn = await asyncpg.connect(
    user="postgres",
    password="Kaleem20252",
    database="postgres",
    host="2600:1f18:2e13:9d0f:6c08:b6c:25a6:73c2",  # IPv6 from nslookup
    port=5432,
    ssl="require"
)

    print("Connected OK")
    await conn.close()

asyncio.run(test())
