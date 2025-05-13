import uvicorn
from loguru import logger
from fastapi import FastAPI, Query
from contextlib import asynccontextmanager

from function_calling_agents.service.pipeline import AgentPipeline

async def startup_hook(app: FastAPI):
    app.state.agento = AgentPipeline()
    
    logger.info("Agento is starting up...")

async def shutdown_hook(app: FastAPI):
    app.state.agento = None
    
    logger.info("Agento is shutting down...")
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_hook(app)
    yield
    await shutdown_hook(app)
    
app = FastAPI(
    title="Agento agent",
    description="Self-built Function calling AI Agent using model Qwen2.5-72B-Instruct",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
    )


@app.get("/calling")
async def calling(query: str = Query(..., description="Query input of user")):
    import time
    start_time = time.time()
    
    final_answer = app.state.agento.run(
        query
    )
    
    elapsed_time = time.time() - start_time
    
    logger.info(f"Agento response: {final_answer}")
    logger.info(f"Time elapse: {elapsed_time:.2f}s")
    
    return {"response": final_answer, "time_elapsed": f"{elapsed_time:.2f}s"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2206, workers=1)









