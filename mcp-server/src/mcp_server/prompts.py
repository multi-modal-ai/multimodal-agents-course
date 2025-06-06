import opik
from loguru import logger

client = opik.Opik()

logger = logger.bind(name="Prompts")


def system_prompt() -> str:
    try:
        prompt = client.get_prompt(name="prompt-system")
        logger.info(f"System prompt loaded. \n {prompt.commit=} \n {prompt.prompt=}")
        return prompt.prompt
    except Exception:
        logger.warning("Nada, not working. Check opik creds playa")
        prompt = "You are a helpful assistant. You need to help the user solve some sport related problems. Your input is {{input}}"
    return prompt


def struct_output_prompt() -> str:
    try:
        prompt = client.get_prompt(name="prompt-struct-output")
        return prompt.prompt
    except Exception:
        logger.warning("Nada, not working. Check opik creds playa")
        prompt = "You are a helpful assistant. You need to help the user solve some sport related problems. Your output is {{output}}"
    return prompt
