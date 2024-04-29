# exponent-server-sdk-python

This repo is maintained by Expo's awesome community :heart_eyes:! So, if you have problems with the code in this repository, please feel free to open an issue, and make a PR. Thanks!

## Installation

```
pip install exponent_server_sdk
```

## Usage

Use to send push notifications to Exponent Experiences from a Python server.

[Full documentation](https://docs.expo.dev/push-notifications/sending-notifications/#http2-api) on the API is available if you want to dive into the details.

Here's an example on how to use this with retries and reporting via [pyrollbar](https://github.com/rollbar/pyrollbar).
```python
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    AsyncPushClient,  # Use the asynchronous version of the PushClient
    PushMessage,
    PushServerError,
    PushTicketError,
)
import os
import httpx
from httpx import HTTPError, NetworkError  # Correct exception handling for httpx

# Optionally providing an access token within a session if you have enabled push security
async with httpx.AsyncClient() as session:
    session.headers.update(
        {
            "Authorization": f"Bearer {os.getenv('EXPO_TOKEN')}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )

    # The async function for sending push messages
    async def send_push_message(token, message, extra=None):
        try:
            response = await AsyncPushClient(session=session).publish(
                PushMessage(to=token,
                            body=message,
                            data=extra))
        except PushServerError as exc:
            # Encountered some likely formatting/validation error.
            rollbar.report_exc_info(
                extra_data={
                    'token': token,
                    'message': message,
                    'extra': extra,
                    'errors': exc.errors,
                    'response_data': exc.response_data,
                })
            raise
        except (NetworkError, HTTPError) as exc:
            # Encountered some Connection or HTTP error - retry a few times in
            # case it is transient.
            rollbar.report_exc_info(
                extra_data={'token': token, 'message': message, 'extra': extra})
            raise self.retry(exc=exc)

        try:
            # We got a response back, but we don't know whether it's an error yet.
            # This call raises errors so we can handle them with normal exception
            # flows.
            response.validate_response()
        except DeviceNotRegisteredError:
            # Mark the push token as inactive
            from notifications.models import PushToken
            await PushToken.objects.filter(token=token).update(active=False)
        except PushTicketError as exc:
            # Encountered some other per-notification error.
            rollbar.report_exc_info(
                extra_data={
                    'token': token,
                    'message': message,
                    'extra': extra,
                    'push_response': exc.push_response._asdict(),
                })
            raise self.retry(exc=exc)

```
