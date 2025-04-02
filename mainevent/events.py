import asyncio
import os
from typing import Any, Callable
from functools import wraps
from traceback import format_exc

import aiostream
import aiohttp
from aiosseclient import aiosseclient


from typing import AsyncGenerator, AsyncIterator, TypeVar


class EventSourceError(Exception):
    pass


SUBSCRIBERS = []
PUBLISHERS = []


async def read_events(event_name: str, host: str, port: int) -> EventSourceError:
    """
    Simple async generator, event source subscriber.
    """
    async for event in aiosseclient(f"http://{host}:{port}/events/subscribe/{event_name}"):
        try:
            yield event
        except asyncio.exceptions.CancelledError() as cancelled:
            raise
    

def subscriber(event_name: str,
                 host: str=os.getenv("EVENT_SOURCE_HOST"), 
                 port: int=os.getenv("EVENT_SOURCE_PORT"),
                 on_error = lambda error: print(format_exc())
                 ):
    """
    Decorates an async function, returns an AsyncGenerator.
    async loops through event topic {event_name}, 
    yielded _wrapped_function(data) where wrapped function has the signature (event:aiostream.Event, *args, **kwargs)=>Any

    Args:
      event_name (required): name of the event/topic.
      interval: minumum time between posted events.
      on_error: sync function, fn (Exception)=>Any, except asyncio.CancelledError
    """
    
    def _subscriber(handler: Callable) -> AsyncIterator[TypeVar('T')]:
        @wraps(handler)
        async def _inner(*args, event=event_name, **kwargs) -> AsyncIterator[TypeVar('T')]:
            async with aiostream.streamcontext(read_events(event_name, host, port)) as stream:
                async for event in stream:
                    try:
                        yield await handler(*args, event=event, **kwargs)
                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        on_error(event)
        
        SUBSCRIBERS.append(_inner())
        return _inner


    return _subscriber


async def send_event(event_name: str,
                     event_data: Any,
                     host: str=os.getenv("EVENT_SOURCE_HOST"), 
                     port: int=os.getenv("EVENT_SOURCE_PORT"), 
                     ):
    async with aiohttp.ClientSession(
        base_url=f"http://{host}:{port}/",
        headers={"X-Event-Name": event_name}
    ) as session:
        try:
            async with session.request("POST", "events/publish/", data=event_data) as resp:
                return await resp.text()
        except Exception as e:
            print(format_exc())


def publisher(event_name: str,
                 interval: float = -1,
                 on_error = lambda error: print(format_exc())):
    """
    Publisher wrapper function; decorates and instantiates an Async Generator,
    then async loops through, publishing the yielded data as a string in the event body.

    Args:
      event_name (required): name of the event/topic.
      interval: minumum time between posted events.
      on_error: sync function, fn (Exception)=>Any, except asyncio.CancelledError
    """

    def _publisher(event_iterable: AsyncGenerator, *args, **kwargs) -> AsyncIterator[TypeVar('T')]:
        async def _inner(*args, **kwargs)-> AsyncIterator[TypeVar('T')]:
            try:
                 async for data in (
                     aiostream.stream.preserve(event_iterable(*args, **kwargs))
                     |aiostream.pipe.spaceout(interval=interval)
                     |aiostream.pipe.map(
                        aiostream.async_(lambda data: send_event(event_name=event_name, event_data=data))
                        ) 
                 ):
                     pass
                 yield
            except asyncio.CancelledError:
                raise
            except Exception as e:
                on_error(e)


        PUBLISHERS.append(_inner())
        return _inner()


    return _publisher
