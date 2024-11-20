import os
import re

def substitute_env_variables(input_string):
    # Regular expression to match ${VALUE} patterns
    pattern = r'\$\{([^}]+)\}'
    
    # Function to replace the match with the environment variable or the original text if not found
    def replace_match(match):
        var_name = match.group(1)
        return os.getenv(var_name, match.group(0))  # Default to original if not found

    # Use re.sub to substitute all occurrences of the pattern in the input string
    return re.sub(pattern, replace_match, input_string)

