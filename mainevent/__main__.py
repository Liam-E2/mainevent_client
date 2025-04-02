import asyncio
import json
import time
from pprint import pprint

from aiosseclient import aiosseclient

from mainevent.mainevent import subscriber, publisher, Pool








if __name__ == '__main__':
    @subscriber("test", host='0.0.0.0', port=9019)
    async def print_egads(event):
        #print(f"Edit ID: {event}")
        return (event.data)


    async def main():
        observed = set()
        async for handle_result in Pool().withDefined().run():
            r = handle_result
            observed.add(r)
            pprint(observed)


    time.sleep(5)
    asyncio.run(main())
