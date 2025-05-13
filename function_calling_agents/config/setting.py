from enum import Enum
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()

class LLMConfig(BaseSettings):
    base_url: str = Field(
        description="Base URL for OpenAI API",
        alias="LLM_URL",
    )
    api_key: str = Field(
        description="API key for OpenAI",
        alias="LLM_KEY",
    )
    model: str = Field(
        description="Model name to be used (e.g., GPT-4)",
        alias="LLM_MODEL",
    )
    temperature: float = Field(
        default=0.0,
        description="Sampling temperature; higher values make output more random",
        alias="TEMPERATURE",
    )
    max_tokens: int = Field(
        default=512,
        alias="MAX_TOKENS",
        description="Maximum number of tokens for API responses",
    )
    top_p: float = Field(
        default=0.95,
        alias="TOP_P",
        description="Nucleus sampling parameter; higher values increase randomness",
    )
    seed: int = Field(default=42, alias="SEED", description="Random seed for sampling")


class ElasticConfig(BaseSettings):
    host: str = Field(
        description="Elasticsearch host",
        alias="ELASTIC_HOST",
    )
    port: int = Field(
        description="Elasticsearch port",
        alias="ELASTIC_PORT",
    )
    index_name: str = Field(
        description="Elasticsearch index",
        alias="ELASTIC_INDEX",
    )
    username: str = Field(
        description="Elasticsearch username",
        alias="ELASTIC_USERNAME",
    )
    password: str = Field(
        description="Elasticsearch password",
        alias="ELASTIC_PASSWORD",
    )

class SearchEngineConfig(BaseSettings):
    api_key: str = Field(
        description="Google Custom Search API key",
        alias="SEARCH_ENGINE_API_KEY",
    )
    search_engine_id: str = Field(
        description="Google Custom Search Engine ID",
        alias="SEARCH_ENGINE_ID",
    )
    max_results: int = Field(
        default=6,
        description="Maximum number of search results to return",
        alias="MAX_SEARCH_RESULTS",
    )
    search_engine_url: str = Field(
        default="https://www.googleapis.com/customsearch/v1",
        description="Google Custom Search API endpoint",
        alias="SEARCH_ENGINE_URL",
    )

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

llm_config = LLMConfig()
search_engine_config = SearchEngineConfig()
