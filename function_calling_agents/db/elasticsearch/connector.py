import logging
from elasticsearch import Elasticsearch
from config.yaml_loader import load_config

from agents.config.setting import elastic_config

config = load_config()
logger = logging.getLogger("elasticsearch_log")

def connect_db() -> Elasticsearch:
    try:
        client = Elasticsearch([{"host": elastic_config.host,
                                 "port": elastic_config.port,
                                 "scheme": "https"}],
                               http_auth=(elastic_config.username, elastic_config.password),
                               timeout=10,
                               max_retries=5,
                               retry_on_timeout=True,
                               verify_certs=False,
                               ssl_show_warn=False)
        
        logger.info("Connected to Elasticsearch")
        return client
        
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        raise e


def check_connection(client: Elasticsearch) -> bool:
    try:
        return client.ping()
    except Exception as e:
        logger.error(f"Ping to Elasticsearch failed: {e}")
        return False
        