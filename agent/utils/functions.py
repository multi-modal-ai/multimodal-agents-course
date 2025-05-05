import base64
import io

import pixeltable as pxt


@pxt.udf
def create_messages_text(
    system_prompt: str,
    memory_context: list[dict],
    current_message: str,
) -> list[dict]:
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(memory_context.copy())

    messages.append({"role": "user", "content": current_message})
    return messages


@pxt.udf
def create_messages_mmodal(
    system_prompt: str,
    memory_context: list[dict],
    current_message: str,
    image: pxt.type_system.Image = None,
) -> list[dict]:
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(memory_context.copy())

    bytes_arr = io.BytesIO()
    image.save(bytes_arr, format="jpeg")
    b64_bytes = base64.b64encode(bytes_arr.getvalue())
    b64_encoded_image = b64_bytes.decode("utf-8")

    # Create content blocks with text and image
    content_blocks = [
        {"type": "text", "text": current_message},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64_encoded_image}"},
        },
    ]

    messages.append({"role": "user", "content": content_blocks})
    return messages
