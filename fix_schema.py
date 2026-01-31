import asyncio
import asyncpg
from backend.config import settings

async def fix_schema():
    dsn = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    conn = await asyncpg.connect(dsn)
    try:
        print("[-] Dropping old constraint 'Messages_room_id_fkey'...")
        await conn.execute('ALTER TABLE "Messages" DROP CONSTRAINT IF EXISTS "Messages_room_id_fkey"')
        
        print("[-] Adding new constraint referencing 'Rooms'...")
        await conn.execute('ALTER TABLE "Messages" ADD CONSTRAINT "Messages_room_id_fkey" FOREIGN KEY (room_id) REFERENCES "Rooms"(id)')
        
        print("[+] Schema fixed successfully.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_schema())
