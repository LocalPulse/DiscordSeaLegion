# config.py

user_data = {}
exp_range = {"min": 5, "max": 15}

def calculate_level(xp):
    return int(xp ** (1/25))