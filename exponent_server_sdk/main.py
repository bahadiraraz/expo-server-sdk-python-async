import os
import httpx
from httpx import HTTPError, NetworkError
from loguru import logger
from dotenv import load_dotenv
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    AsyncPushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)

logger.add("debug.log", rotation="1 week", compression="zip")
load_dotenv()
logger.debug("Using Expo Token: {}", os.getenv('EXPO_TOKEN'))


async def send_push_message(token, message, extra=None):
    async with httpx.AsyncClient(headers={
        "Authorization": f"Bearer {os.getenv('EXPO_TOKEN')}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }) as session:
        try:
            response = await AsyncPushClient(session=session).publish(
                PushMessage(to=token, body=message, data=extra, sound="default"))
            response.validate_response()
        except PushServerError as exc:
            logger.error("Push server error: {}", exc)
            raise
        except (NetworkError, HTTPError) as exc:
            logger.error("Network or HTTP error: {}", exc)
            raise
        except DeviceNotRegisteredError:
            logger.warning("Device not registered, deactivating token: {}", token)

        except PushTicketError as exc:
            logger.error("Push ticket error: {}", exc)
            raise

async def main():
    token = "ExponentPushToken[TOKEN]"
    message = "HI! This is a test message."
    extra_parameters = {"key": "value"}
    await send_push_message(token, message, extra_parameters)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
