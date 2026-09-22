import asyncio
import websockets
import time
import struct
import json
import urllib.request
import os

def get_token():
    data = json.dumps({
        "email": "vlm_test@example.com",
        "password": os.getenv("TEST_PASSWORD")
    }).encode()

    request = urllib.request.Request(
        "http://127.0.0.1:8001/login",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode())

    return result["access_token"]


async def main():

    token = get_token()
    print("JWT generated successfully")

    with open("/tmp/test_screen.jpg", "rb") as f:
        image = f.read()

    uri = f"ws://127.0.0.1:8001/ws/screen?token={token}"

    print("Connecting to /ws/screen...")

    async with websockets.connect(uri) as websocket:
        print("Connected to /ws/screen")

        captured_at_ms = int(time.time() * 1000)

        message = (
            struct.pack("!Q", captured_at_ms)
            + image
        )

        await websocket.send(message)

        print("Screen frame sent")

        await asyncio.sleep(15)


if __name__ == "__main__":
    asyncio.run(main())
