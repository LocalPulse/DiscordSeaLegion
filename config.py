# config.py

user_data = {}
exp_range = {"min": 5, "max": 15}

role_assignments = {
    "duty_guard": {
        5: "Дозорный 5 уровня",
        10: "Дозорный 10 уровня",
    },
    "pirate": {
        5: "Пират 5 уровня",
        10: "Пират 10 уровня",
    }
}

def calculate_level(xp):
    return int(xp ** (1/3))