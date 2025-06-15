import asyncio
import os
import time
from enum import Enum

import aiohttp
import streamlit as st


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


API_BASE_URL = "http://agent-api:8080"
DEFAULT_RETRY_INTERVAL_SEC = 5
LOADING_SPINNER_FRAMES = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]

os.makedirs("videos", exist_ok=True)
st.set_page_config(page_title="Chat & Video Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    /* ... (Your existing CSS for video cards and layout) ... */

    /* Add some specific styles for task status if needed */
    .stStatusWidget { /* Streamlit's default status widget class */
        font-size: 1.1em;
        font-weight: bold;
        color: #007bff;
    }
</style>
""",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "processing_task_id" not in st.session_state:
    st.session_state.processing_task_id = None
if "processing_status" not in st.session_state:
    st.session_state.processing_status = None
if "last_checked_time" not in st.session_state:
    st.session_state.last_checked_time = 0


@st.cache_data(show_spinner=False)
def get_async_session():
    loop = asyncio.get_event_loop()
    return aiohttp.ClientSession(loop=loop)


async def _poll_task_status(session, task_id_to_poll, status_placeholder):
    while True:
        try:
            async with session.get(f"{API_BASE_URL}/task-status/{task_id_to_poll}") as status_resp:
                if status_resp.status != 200:
                    status_placeholder.error("Error checking task status.")
                    return TaskStatus.FAILED  # Indicate failure to break loop
                status_data = await status_resp.json()
                current_status = TaskStatus(status_data.get("status"))

                if current_status == TaskStatus.IN_PROGRESS:
                    status_placeholder.info(f"Processing video... Status: {current_status.value}")
                elif current_status == TaskStatus.COMPLETED:
                    status_placeholder.success("Video processed successfully!")
                    return current_status  # Break loop
                elif current_status == TaskStatus.FAILED:
                    status_placeholder.error("Video processing failed.")
                    return current_status  # Break loop
                else:
                    status_placeholder.warning(f"Unknown status: {current_status.value}")

        except Exception as e:
            status_placeholder.error(f"Error during polling: {e}")
            return TaskStatus.FAILED  # Indicate failure to break loop

        time.sleep(DEFAULT_RETRY_INTERVAL_SEC)
        st.rerun()


col1, col2 = st.columns([3, 1], gap="medium")

with col1:
    st.header("💬 Chat Window")
    st.write("---")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    uploaded_file = st.file_uploader("Upload your video (MP4, max 100MB)", type=["mp4"])

    if uploaded_file is not None and st.session_state.processing_task_id is None:
        dest_path = os.path.join("videos", uploaded_file.name)
        with open(dest_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.video_path = dest_path

        st.session_state.messages.append({"role": "user", "content": f"Uploaded video: {uploaded_file.name}"})
        with st.chat_message("user"):
            st.markdown(f"Uploaded video: {uploaded_file.name}")

        if st.button("Process Video"):
            st.session_state.processing_status = TaskStatus.PENDING.value
            st.session_state.processing_task_id = None
            st.session_state.last_checked_time = time.time()
            st.session_state.messages.append({"role": "user", "content": "Processing video..."})
            with st.chat_message("user"):
                st.markdown("Processing video... Please wait.")
        try:
            status_placeholder = st.empty()
            status_placeholder.info("Sending video for processing...")
            async_session = get_async_session()  # Get the cached session

            # Make the async request
            response = asyncio.run(
                async_session.post(
                    f"{API_BASE_URL}/process-video",
                    json={"video_path": dest_path},
                )
            )
            response.raise_for_status()
            data = asyncio.run(response.json())
            task_id = data.get("task_id")
            st.session_state.processing_task_id = task_id
            st.session_state.processing_status = TaskStatus.IN_PROGRESS.value
            status_placeholder.empty()
            st.rerun()
        except aiohttp.ClientError as e:
            st.error(f"Error connecting to API: {e}")
            st.session_state.processing_task_id = None
            st.session_state.video_path = None
        except Exception as e:
            st.error(f"Error initiating video processing: {e}")
            st.session_state.processing_task_id = None
            st.session_state.video_path = None

    if st.session_state.processing_task_id:
        status_message_placeholder = st.empty()
        status_message_placeholder.markdown(f"**Video Processing Status:** {st.session_state.processing_status}")

        if st.session_state.processing_status in [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]:
            if time.time() - st.session_state.last_checked_time > DEFAULT_RETRY_INTERVAL_SEC:
                with st.spinner("Checking processing status..."):
                    async_session = get_async_session()
                    current_poll_status = asyncio.run(
                        async_session.get(f"{API_BASE_URL}/task-status/{st.session_state.processing_task_id}")
                    )
                    if current_poll_status.status == 200:
                        status_data = asyncio.run(current_poll_status.json())
                        st.session_state.processing_status = TaskStatus(status_data.get("status")).value
                        st.session_state.last_checked_time = time.time()  # Update last checked time
                    else:
                        st.error("Could not retrieve task status.")
                        st.session_state.processing_status = TaskStatus.FAILED.value
                st.rerun()
            else:
                time.sleep(1)
                st.rerun()

        if st.session_state.processing_status == TaskStatus.COMPLETED.value:
            status_message_placeholder.success("Video processing completed! You can now chat about the video.")
        elif st.session_state.processing_status == TaskStatus.FAILED.value:
            status_message_placeholder.error("Video processing failed. Please try again.")
            st.session_state.processing_task_id = None

    prompt = st.chat_input("Ask something about the video...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if st.session_state.processing_status == TaskStatus.COMPLETED.value and st.session_state.video_path:
            try:
                async_session = get_async_session()
                response = asyncio.run(
                    async_session.post(
                        f"{API_BASE_URL}/chat",
                        json={"message": prompt, "video_path": st.session_state.video_path},
                    )
                )
                response.raise_for_status()
                data = asyncio.run(response.json())
                bot_response = data["response"]
                with st.chat_message("assistant"):
                    st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            except aiohttp.ClientError as e:
                error_msg = f"Error communicating with API: {e}"
                with st.chat_message("assistant"):
                    st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"An unexpected error occurred: {e}"
                with st.chat_message("assistant"):
                    st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            bot_response = "Please upload and wait for the video to be processed before chatting."
            with st.chat_message("assistant"):
                st.info(bot_response)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})


with col2:
    st.header("📺 Featured Videos")
    st.write("---")

    videos = [
        # ... (Your existing video list) ...
        {
            "title": "Introduction to Python",
            "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",  # Changed to actual YT link
            "description": "A quick introduction to the Python programming language basics.",
            "thumbnail": "https://i.ytimg.com/vi/rfscVS0vtbw/hq720.jpg",
        },
        {
            "title": "Machine Learning Explained",
            "url": "https://www.youtube.com/watch?v=ukzFI9rgwfU",
            "description": "Understanding the core concepts of machine learning in simple terms.",
            "thumbnail": "https://i.ytimg.com/vi/ukzFI9rgwfU/hq720.jpg",
        },
        {
            "title": "Data Science Project Walkthrough",
            "url": "https://www.youtube.com/watch?v=ua-CiDNNj30",
            "description": "A step-by-step guide through a real-world data science project.",
            "thumbnail": "https://i.ytimg.com/vi/ua-CiDNNj30/hq720.jpg",
        },
        {
            "title": "Web Development Basics",
            "url": "https://www.youtube.com/watch?v=pB0yJ7-0q04",
            "description": "Get started with HTML, CSS, and JavaScript for web development.",
            "thumbnail": "https://i.ytimg.com/vi/pB0yJ7-0q04/hq720.jpg",
        },
    ]

    st.markdown('<div class="video-grid-container">', unsafe_allow_html=True)
    num_videos_per_row = 2
    for i in range(0, len(videos), num_videos_per_row):
        cols_video = st.columns(num_videos_per_row)
        for j in range(num_videos_per_row):
            if i + j < len(videos):
                video_data = videos[i + j]
                with cols_video[j]:
                    st.markdown('<div class="video-card">', unsafe_allow_html=True)
                    st.video(video_data["url"], format="video/mp4")
                    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
