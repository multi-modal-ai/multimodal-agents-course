import asyncio
import os
import shutil
from enum import Enum
from typing import List

import aiohttp
import chainlit as cl


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


API_BASE_URL = "http://0.0.0.0:8080"  # Adjust to your FastAPI server address
DEFAULT_RETRY_INTERVAL_SEC = 10
LOADING_SPINNER_FRAMES = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
LOADING_SPINNER_TASK = None

os.makedirs("videos", exist_ok=True)


async def spinner_func(base_msg: str, frames: List[str], interval: float = 0.8) -> None:
    msg = cl.Message(content=base_msg)
    await msg.send()

    progress = 0
    bar_length = 12

    try:
        while True:
            current_frame = frames[progress % len(frames)]
            progress_bar = ("▣" * (progress % bar_length)).ljust(bar_length, "▢")
            msg.content = f"{current_frame} {base_msg}\n{progress_bar}"
            await msg.update()

            progress += 1
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        await msg.update(content=base_msg)


@cl.on_chat_start
async def start():
    global LOADING_SPINNER_TASK
    files = None

    while not files:
        files = await cl.AskFileMessage(
            content="Please upload your video to begin!",
            accept=[".mp4"],
            max_size_mb=100,
        ).send()

    video_file = files[0]
    dest_path = os.path.join("videos", video_file.name)
    shutil.move(video_file.path, dest_path)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/process-video",
                json={"video_path": dest_path},
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    await cl.Message(content=f"Error from API: {error_text}").send()
                    return

                data = await response.json()
                task_id = data.get("task_id")
                while True:
                    async with session.get(f"{API_BASE_URL}/task-status/{task_id}") as status_resp:
                        if status_resp.status != 200:
                            await cl.Message(content="Error checking task status").send()
                            break
                        status_data = await status_resp.json()
                        status = status_data.get("status")

                        if TaskStatus(status) == TaskStatus.IN_PROGRESS:
                            if LOADING_SPINNER_TASK is None or LOADING_SPINNER_TASK.done():
                                LOADING_SPINNER_TASK = asyncio.create_task(
                                    spinner_func(
                                        base_msg="Processing your video...",
                                        frames=LOADING_SPINNER_FRAMES,
                                        interval=0.5,
                                    )
                                )
                        elif TaskStatus(status) == TaskStatus.COMPLETED:
                            if LOADING_SPINNER_TASK:
                                LOADING_SPINNER_TASK.cancel()
                                try:
                                    await LOADING_SPINNER_TASK
                                except asyncio.CancelledError:
                                    pass
                            await cl.Message(content="Video processed successfully!").send()
                            break
                        elif TaskStatus(status) == TaskStatus.FAILED:
                            if LOADING_SPINNER_TASK:
                                LOADING_SPINNER_TASK.cancel()
                                try:
                                    await LOADING_SPINNER_TASK
                                except asyncio.CancelledError:
                                    pass
                            await cl.Message(content="Video processing failed.").send()
                            break
                    await asyncio.sleep(DEFAULT_RETRY_INTERVAL_SEC)  # wait before polling

            cl.user_session.set("video_path", dest_path)

        except Exception as e:
            await cl.Message(content=f"Error handling video file: {str(e)}").send()


@cl.on_message
async def main(message: cl.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/chat",
                json={"message": message.content, "video_path": cl.user_session.get("video_path")},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    await cl.Message(content=data["response"]).send()
                else:
                    error_text = await response.text()
                    await cl.Message(content=f"Error from API: {error_text}").send()
    except Exception as e:
        await cl.Message(content=f"Error communicating with API: {str(e)}").send()
