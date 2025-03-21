# Manage multiplaylists with event loop
from fastapi import FastAPI
import uvicorn
import asyncio

app = FastAPI()

class User:
    is_running = True

    def stop(self):
        self.is_running = False

users = {}

@app.post("/do/{id}")
async def lets_do(id: str):
    users[id] = asyncio.Event()
    users[id].set()

    asyncio.create_task(do(id))

@app.post("/stop/{id}")
async def stop_it(id: str):
    users[id].clear()

async def do(id):
    event = users[id]

    while event.is_set():
        print(f"Do: {id}")
        await asyncio.sleep(5)

async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8080)
    server = uvicorn.Server(config)

    await asyncio.create_task(server.serve())   

if __name__ == "__main__":
    asyncio.run(main())