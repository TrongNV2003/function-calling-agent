import time
import argparse
from loguru import logger
from agents.service.pipeline import AgentPipeline

def main():
    agento = AgentPipeline()
    
    parser = argparse.ArgumentParser(description="Function calling AI Agents.")
    parser.add_argument("--query", default="Tính 999 chia 765", type=str, help="Query input of user")
    args = parser.parse_args()

    start_time = time.time()

    final_answer = agento.run(args.query)
    
    elapsed_time = time.time() - start_time

    logger.info(f"Agento response: {final_answer}")
    logger.info(f"Time elapse: {elapsed_time:.2f}s")

if __name__ == "__main__":
    main()

