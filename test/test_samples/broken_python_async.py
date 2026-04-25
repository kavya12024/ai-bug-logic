import asyncio
import time

async def fetch_data(id):
    # This is a blocking call inside an async function!
    # It will block the entire event loop, preventing concurrency.
    time.sleep(2)
    print(f"Fetched data for ID: {id}")
    return {"id": id, "data": "Some data payload"}

async def process_all():
    print("Starting concurrent fetches...")
    t1 = asyncio.create_task(fetch_data(1))
    t2 = asyncio.create_task(fetch_data(2))
    results = [t1, t2]
    for res in results:
        print(f"Result: {res['data']}")

if __name__ == '__main__':
    asyncio.run(process_all())