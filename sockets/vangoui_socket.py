import asyncio
import websockets
import json
import hashlib
import random
import string

# handles the client web socket connection
def generate_client_id():
    # Generate a random string
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    # Create an MD5 hash of the random string
    return hashlib.md5(random_string.encode()).hexdigest()

async def handle_connection(websocket, path):
    client_id = generate_client_id()
    print(f"New connection with client ID: {client_id}")

    try:
        async for message in websocket:
            if isinstance(message, bytes):
                # Handle binary message
                pass
            else:
                # Handle text message
                data = json.loads(message)
                message_type = data.get("type")

                if message_type == "status":
                    response = {
                        "type": "status",
                        "data": {
                            "sid": client_id,
                            "status": "{'exec_info': {'queue_remaining': 0}"
                        }
                    }
                    await websocket.send(json.dumps(response))
                # Add more cases here to handle other message types

                elif message_type == "progress":
                    pass

                else:
                    print(f"Unknown message type {message_type}")

    except websockets.ConnectionClosed:
        print("Connection closed")
    except Exception as e:
        print(f"Error handling connection: {e}")

start_server = websockets.serve(handle_connection, "localhost", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
