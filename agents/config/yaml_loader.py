import yaml

def load_config() -> dict:
    """Load configuration from a YAML file."""
    try:
        with open("../config.yaml", "r") as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise Exception(f"Configuration file not found.")
    except yaml.YAMLError as e:
        raise Exception(f"Error parsing YAML file: {e}")
