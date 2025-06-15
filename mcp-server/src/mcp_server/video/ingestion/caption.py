from groq import AsyncGroq, RateLimitError
from PIL import Image
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from mcp_server.config import get_settings
from mcp_server.video.ingestion.tools import encode_image

settings = get_settings()

class VisualCaptioningModel:
    """A model for generating captions from images using Groq's vision-language models.

    This class provides functionality to caption images using Groq's VLM models through their API.

    Args:
        model_name (str): The name of the Groq model to use. Defaults to settings.GROQ_VLM_MODEL.

    Attributes:
        model_name (str): The name of the Groq model being used.
        client (Groq): The Groq API client instance.
    """

    def __init__(self, model_name: str = settings.GROQ_VLM_MODEL):
        self.model_name = model_name
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential_jitter(initial=10, max=60),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def caption(self, image: Image.Image | str, prompt: str) -> str:
        """Generate a caption for the given image using the specified prompt.

        Args:
            image (Union[Image, str]): The input image, either as a PIL Image object or a path string.
            prompt (str): The prompt text to guide the caption generation.

        Returns:
            str: The generated caption text.

        Note:
            If image is provided as a string, it will be loaded and converted to RGB format.
        """
        base64_image = encode_image(image)

        chat_completion = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model=settings.GROQ_VLM_MODEL,
        )
        return chat_completion.choices[0].message.content

    def __repr__(self):
        return f"VisualCaptioningModel(model_name={self.model_name})"
