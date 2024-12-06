

def parse_configs():
    """
    Parse the configuration file and store the key-value pairs in a dictionary.
    """
    configs: dict = {}
    with open('config.conf', 'r') as f:
        for line in f:
            if not line.startswith('#'):
                line_data = line.replace(' ', '').split('#', 1)[0]
                if '=' in line_data:
                    key, value = line_data.split('=', 1)
                    configs[key] = value[1:-1]
                
                
    return configs






            


            