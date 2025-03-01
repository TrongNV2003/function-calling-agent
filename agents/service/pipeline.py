import json
from loguru import logger
from collections import deque

from agents.service.agent import Agento
from agents.service.prompts import FUNCTION_CALLING_PROMPT, LIST_FUNCTION_PROMPT

class AgentPipeline:
    def __init__(self):
        self.agent = Agento(prompt_template=FUNCTION_CALLING_PROMPT)
        self.previous_actions = deque(maxlen=3)
        self.max_steps_thinking = 9

    
    def run(self, query: str) -> str:
        history = ""
        thinking = ""
        prompt = self.agent.inject_prompt(query, thinking, history, LIST_FUNCTION_PROMPT)
        
        for step in range(self.max_steps_thinking):
            logger.info(f"=== Bước {step + 1}/{self.max_steps_thinking} ===")
            response = self.agent.call_llm(prompt)

            # Case 1: Respond final answer
            if "final_answer" in response:
                logger.info("=== Final output ===")
                print(response["final_answer"])
                return response["final_answer"]
            
            # Case 2: Reasoning and planning
            elif "thought" in response:
                logger.info("=== LLM suy nghĩ: {} ===".format(response["thought"]))
                thinking += f"\n<think>\n{json.dumps(response, ensure_ascii=False)}\n</think>"
                logger.info("=== Cập nhật lịch sử suy nghĩ ===\n{}".format(thinking))
                prompt = self.agent.inject_prompt(query, thinking, history, LIST_FUNCTION_PROMPT)
                continue

            # Case 3: Calling function
            elif "function_call" in response:
                logger.info("=== Action execution ===")
                print(response)
                function_call = response["function_call"]

                action_key = json.dumps(function_call)

                self.previous_actions.append(action_key)

                if len(self.previous_actions) == 3 and len(set(self.previous_actions)) == 1:
                    logger.warning("=== Agent got dumps :v")
                    return "Error: Agent got repeated action."

                func_output = self.agent.call_tool(function_call["function"], function_call["arguments"])
                history += f"\n{func_output}"
                logger.info("=== Update result ===")
                print(history)
                prompt = self.agent.inject_prompt(query, thinking, history, LIST_FUNCTION_PROMPT)
            
            else:
                logger.error("=== Chìm thuyền rồi thầy ơi, ọc ọc ọc... ===")

        logger.error("=== Max retries processed  ===")
