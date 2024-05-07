# exponent-server-sdk-python-async

This repo is made for the async version of the [exponent-server-sdk-python](https://github.com/expo-community/expo-server-sdk-python) made by [Bahadır Araz](https://github.com/bahadiraraz).

## Installation

```
pip install exponent-server-sdk-async
```

## Usage
Use to send push notifications to Exponent Experiences from a Python server.
[Full documentation](https://docs.expo.dev/push-notifications/sending-notifications/#http2-api) on the API is available if you want to dive into the details.
```python
import asyncio
import os
import httpx
from loguru import logger
from dotenv import load_dotenv
from exponent_server_sdk_async import (
    AsyncPushClient,
    PushMessage,
    DeviceNotRegisteredError,
    PushTicketError,
    PushServerError
)

# Logger setup
logger.add("debug.log", rotation="1 week", compression="zip")
load_dotenv()
logger.debug("Using Expo Token: {}", os.getenv('EXPO_TOKEN'))


async def send_push_message_to_multiple(tokens, message, extra, title, navigate_to=None):
    async with httpx.AsyncClient(headers={
        "Authorization": f"Bearer {os.getenv('EXPO_TOKEN')}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }) as session:
        push_client = AsyncPushClient(session=session)
        push_messages = [
            PushMessage(
                to=token,
                body=message,
                data={'extra': extra, 'navigateTo': navigate_to},
                badge=1,
                title=title,
                sound="default"
            ) for token in tokens
        ]
        try:
            push_tickets = await push_client.publish_multiple(push_messages)
            for push_ticket in push_tickets:
                if push_ticket.is_success():
                    logger.info("Notification sent successfully to: {}", push_ticket.push_message.to)
                else:
                    logger.warning("Failed to send notification to: {}, Error: {}", push_ticket.push_message.to, push_ticket.message)
        except PushServerError as exc:
            logger.error("Push server error: {}", exc)
            raise
        except DeviceNotRegisteredError as exc:
            logger.error("Device not registered error: {}", exc)
            raise
        except PushTicketError as exc:
            logger.error("Push ticket error: {}", exc)
            raise


async def main():
    tokens = [
        "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
        "ExponentPushToken[yyyyyyyyyyyyyyyyyyyyyy]",
        "ExponentPushToken[zzzzzzzzzzzzzzzzzzzzzz]"
    ]
    extra_parameters = {"key": "value"}

    # Send a simple push message to multiple recipients
    await send_push_message_to_multiple(tokens, "Hello Multi-User", extra_parameters, "Greeting")

    # Navigate to home data for multiple recipients
    await send_push_message_to_multiple(tokens, "Navigate to home", extra_parameters, "Home", "/(tabs)/(home)")


if __name__ == "__main__":
    asyncio.run(main())
```
