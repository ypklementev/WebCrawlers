import uuid
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from crawler import AsyncCrawler

app = FastAPI()
tasks = {}  # task_id -> {status, crawler, task, results}


class CrawlRequest(BaseModel):
    url: str


@app.post("/crawl")
async def crawl(req: CrawlRequest):
    task_id = str(uuid.uuid4())

    crawler = AsyncCrawler(req.url, max_tasks=50)

    # создаем asyncio task, но НЕ await'им
    crawler_task = asyncio.create_task(crawler.run())

    tasks[task_id] = {
        "status": "running",
        "crawler": crawler,
        "task": crawler_task,
        "results": None,
    }

    return {"task_id": task_id}


@app.websocket("/ws/{task_id}")
async def ws_progress(ws: WebSocket, task_id: str):
    await ws.accept()

    if task_id not in tasks:
        await ws.send_json({"type": "error", "message": "invalid task"})
        await ws.close()
        return

    entry = tasks[task_id]
    crawler = entry["crawler"]
    crawler_task = entry["task"]

    while True:
        # если crawler еще работает
        if not crawler_task.done():
            processed = len(crawler.visited)
            found = processed + crawler.queue.qsize()

            await ws.send_json({
                "type": "progress",
                "processed": processed,
                "found": found,
            })

        else:
            # crawler закончил — получаем результат
            try:
                result = crawler_task.result()
                entry["results"] = result
                entry["status"] = "finished"

                await ws.send_json({
                    "type": "finished",
                    "results": result
                })
            except Exception as e:
                entry["status"] = "error"
                entry["results"] = str(e)
                await ws.send_json({
                    "type": "error",
                    "message": str(e)
                })

            break

        await asyncio.sleep(0.2)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)