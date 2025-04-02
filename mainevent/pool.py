import os
from typing import AsyncIterator
from typing_extensions import Self

import aiostream


class Pool:
    """
    
    """
    def __init__(self,
                 host=None,
                 port=None) -> None:
        
        self.host = os.getenv("EVENT_SOURCE_HOST") if host is None else host
        self.port = os.getenv("EVENT_SOURCE_PORT") if port is None else port
        self.subscribers = []
        self.publishers = []
    

    async def run(self) -> AsyncIterator:
        combined = aiostream.stream.merge(*self.subscribers, *self.publishers)
        async with combined.stream() as streamer:
            async for event in streamer:
                yield event


    def withSubscriber(self, subscriber: AsyncIterator) -> Self:
        self.subscribers.append(subscriber())
        return self
    

    def withPublisher(self, publisher: AsyncIterator) -> Self:
        self.publishers.append(publisher())
        return self

    
    def withDefined(self):
        """
        Collects all publishers/subscribers appended to events.PUBLISHERS and events.SUBSCRIBERS
        """
        from .events import PUBLISHERS, SUBSCRIBERS
        self.publishers.extend(PUBLISHERS)
        self.subscribers.extend(SUBSCRIBERS)
        return self
