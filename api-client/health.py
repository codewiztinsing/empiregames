import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:5000/"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            await websocket.send("Hello, server!")
            response = await websocket.recv()
            print(f"Received from server: {response}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
