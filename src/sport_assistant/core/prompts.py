import opik
from loguru import logger

class Prompt:
    def __init__(self, name: str, prompt: str) -> None:
        self.name = name

        try:
            self.__prompt = opik.Prompt(name=name, prompt=prompt)
        except Exception:
            logger.warning(
                "Can't use Opik to version the prompt (probably due to missing or invalid credentials). Falling back to local prompt. The prompt is not versioned, but it's still usable."
            )

            self.__prompt = prompt

    @property
    def prompt(self) -> str:
        if isinstance(self.__prompt, opik.Prompt):
            return self.__prompt.prompt
        else:
            return self.__prompt

    def __str__(self) -> str:
        return self.prompt

    def __repr__(self) -> str:
        return self.__str__()
    
__SPORT_ASSISTANT_SYSTEM_PROMPT = """
You are a sport assistant. You need to help the user solve some sport related problems.
You are a Real Madrid fan and you hate FC Barcelona.
"""

SPORT_ASSISTANT_SYSTEM_PROMPT = Prompt(
    name="sport_assistant_system_prompt",
    prompt=__SPORT_ASSISTANT_SYSTEM_PROMPT,
)
