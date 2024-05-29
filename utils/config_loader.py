import yaml

def load_config(file_path='config.yaml'):
    """
    Load configuration from a YAML file.

    Args:
        file_path (str): The path to the configuration file.

    Returns:
        dict: The configuration dictionary.
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
