import asyncio
from pathlib import Path

from fastmcp import Client

if __name__ == "__main__":
    video_path = "multimodal-agents-course/.cache/por_vs_esp_5min/2018_portugal_vs_spain_T0h0m_0h5m.mp4"

    # video_processor = VideoProcessor(video_clip_length=60, split_fps=1.0, audio_chunk_length=30)
    # video_processor.setup_table(video_name=video_path)
    # video_processor.add_video(video_path=video_path)
    # print(f"Video {video_path} added successfully.")

    async def mcp_loop():
        mcp_client = Client("http://127.0.0.1:8080/sse")
        async with mcp_client:
            tools = await mcp_client.list_tools()
            # TODO: keep it for now, remote later, add debug flag maybe
            print(f"Available tools: {' '.join(tool.name for tool in tools)}")
            # FIXME: currently, make_video from pxt handles videos in-memory, str(obj) yields path on disk
            vid_clips_paths = await mcp_client.call_tool(
                "get_clip_by_caption_sim",
                {
                    "video_name": Path(video_path).stem,
                    "user_query": "Cristiano Ronaldo",
                    "top_k": 1,
                },
            )

            print(f"Video clips raw_path: {' '.join(str(clip) for clip in vid_clips_paths)}")

    asyncio.run(mcp_loop())
