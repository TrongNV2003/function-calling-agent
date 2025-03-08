import json
from loguru import logger
from collections import deque

from agents.service.agent import Agento
from agents.service.prompts import FUNCTION_CALLING_PROMPT, LIST_FUNCTION_PROMPT

class AgentPipeline:
    def __init__(self):
        self.agent = Agento(prompt_template=FUNCTION_CALLING_PROMPT)
        self.previous_actions = deque(maxlen=3)
        self.max_steps_thinking = 20

    
    def run(self, query: str, step_callback=None, show_prompt: bool = False) -> str:
        history = ""
        thinking = ""
        steps = []
        prompt = self.agent.inject_prompt(query, thinking, history, LIST_FUNCTION_PROMPT)
        
        for step in range(self.max_steps_thinking):
            logger.info(f"=== Bước {step + 1}/{self.max_steps_thinking} ===")
            response = self.agent.call_llm(prompt, show_prompt=show_prompt)

            # Case 1: Respond final answer
            if "final_answer" in response:
                logger.info("=== Final output ===")
                print(response["final_answer"])
                step_data = {"step": step + 1, "type": "final_answer", "content": response["final_answer"]}
                if step_callback:
                    step_callback(step_data)
                else:
                    steps.append(step_data)
                break
            
            # Case 2: Reasoning and planning
            elif "thought" in response:
                logger.info("=== LLM thinking ===")
                print(response["thought"])
                thinking += f"\n<think>\n{json.dumps(response, ensure_ascii=False)}\n</think>"
                step_data = {"step": step + 1, "type": "thinking", "content": response["thought"]}
                if step_callback:
                    step_callback(step_data)
                else:
                    steps.append(step_data)
                logger.info("=== Cập nhật lịch sử thinking ===\n{}".format(thinking))
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
                    logger.warning("=== Agent got dumps :v ===")
                    step_data = {"step": step + 1, "type": "error", "content": "Error: Agent got repeated action."}
                    if step_callback:
                        step_callback(step_data)
                    else:
                        steps.append(step_data)
                    break

                # Action step
                step_data = {"step": step + 1, "type": "action", "content": f"Call {function_call['function']} with {function_call['arguments']}"}
                if step_callback:
                    step_callback(step_data)
                else:
                    steps.append(step_data)
                

                # Execution step
                func_output = self.agent.call_tool(function_call["function"], function_call["arguments"])
                history += f"\n{func_output}"
                step_data = {"step": step + 1, "type": "execution", "content": func_output}
                if step_callback:
                    step_callback(step_data)
                else:
                    steps.append(step_data)

                logger.info("=== Update result ===")
                print(history)
                prompt = self.agent.inject_prompt(query, thinking, history, LIST_FUNCTION_PROMPT)
            
            else:
                logger.error("=== Chìm thuyền rồi thầy ơi, ọc ọc ọc... ===")
                step_data = {"step": step + 1, "type": "error", "content": "Unknown response format."}
                if step_callback:
                    step_callback(step_data)
                else:
                    steps.append(step_data)
                break

        if step >= self.max_steps_thinking - 1:
            logger.error("=== Max retries processed ===")
            step_data = {"step": self.max_steps_thinking, "type": "error", "content": "Max retries reached."}
            if step_callback:
                step_callback(step_data)
            else:
                steps.append(step_data)

        if not step_callback:
            return {"query": query, "steps": steps}
