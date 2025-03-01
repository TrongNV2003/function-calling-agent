import logging
from elasticsearch import Elasticsearch
from config.yaml_loader import load_config

config = load_config()
logger = logging.getLogger("elasticsearch_log")

def connect_db() -> Elasticsearch:
    try:
        client = Elasticsearch([{"host": config["elasticsearch"]["host"], 
                                 "port": config["elasticsearch"]["port"], 
                                 "scheme": "https"}],
                               http_auth=(config["elasticsearch"]["http_auth"]["username"], config["elasticsearch"]["http_auth"]["password"]), 
                               timeout=10, 
                               max_retries=5, 
                               retry_on_timeout=True,
                               verify_certs=False,
                               ssl_show_warn=False)

        return client
        
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch {e}")
        