from openai import OpenAI
from loguru import logger
from typing import List, Optional, Union

from agents.service.utils import parse_response
from agents.config.setting import llm_config, Role
from agents.functions.calculator import Calculator
from agents.functions.search_engine import SearchEngine
from agents.service.prompts import SYSTEM_PROMPT


class Agento:
    def __init__(
        self,
        llm: Optional[OpenAI] = None,
        prompt_template: Optional[str] = None,
    ):
        if llm is None:
            llm = OpenAI(api_key=llm_config.api_key, base_url=llm_config.base_url)
            
        self.llm = llm
        self.prompt_template = prompt_template

        self.tools = [Calculator(), SearchEngine()]

    def call_llm(self, prompt: str) -> dict:
        logger.info("=== Prompt ===")
        print(prompt)
        response = self.llm.chat.completions.create(
            seed=llm_config.seed,
            temperature=llm_config.temperature,
            top_p=llm_config.top_p,
            model=llm_config.model,
            messages=[
                {"role": Role.SYSTEM, "content": SYSTEM_PROMPT},
                {"role": Role.USER, "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        logger.info("=== Agent response ===")
        print(content)
        return parse_response(content)

    def call_tool(self, function_name: str, arguments: dict) -> str:
        print(f"=== Calling function: {function_name} với arguments: {arguments} ===")
        for tool in self.tools:
            if tool.name == function_name:
                try:
                    result = tool.forward(**arguments)
                    output = f"<observe>\nKết quả từ hàm {function_name}: {result}\n</observe>"
                    logger.info("=== Kết quả từ tool ===")
                    print(output)
                    return output
                except Exception as e:
                    logger.error(f"=== Lỗi khi gọi tool {function_name}: {str(e)} ===")
                    raise
        return "Tool not available, please check the function name or tool availability."

    def inject_prompt(
        self,
        text: str,
        thinking: str = "",
        history: str = "",
        list_functions: Optional[Union[str, List[str]]] = None,
    ) -> str:
        prompt_str = self.prompt_template.format(
            text=text,
            thinking=thinking,
            history=history,
            list_functions=list_functions,
        )
        return prompt_str



