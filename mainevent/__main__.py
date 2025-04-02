import asyncio
import json
import time
from pprint import pprint

from aiosseclient import aiosseclient

from mainevent.mainevent import subscriber, publisher, Pool








if __name__ == '__main__':
    @subscriber("example")
    async def print_egads(event):
        #print(f"Edit ID: {event}")
        return (event.data)


    @publisher("example", interval=3)
    async def test_events():
        async for event in aiosseclient('https://stream.wikimedia.org/v2/stream/recentchange'):
            if 'Russia' in (data := json.loads(event.data).get('title', '')):
                continue
            yield json.dumps(data)


    async def main():
        observed = set()
        async for handle_result in Pool().withDefined().run():
            r = handle_result
            observed.add(r)
            pprint(observed)


    time.sleep(5)
    asyncio.run(main())
