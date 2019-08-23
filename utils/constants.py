'''
Util file for static classes containing constants. (Not for messages)
'''

# Sleep Time
SLEEP_TIME = 0

# Play modes
class Modes:
    PLAY = "PLAY"
    TRIAL = "TRIAL"

# Game play strings
class Gameplay:
    POWER_YES = "y"
    POWER_NO = "n"
    CANCELLED = "Cancelled"

# Strategies
class Strategies:
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    RANDOM_FOREST = "RANDOM_FOREST"
    NEURAL_NET = "NEURAL_NET"
    LOGISTIC = "LOGISTIC"
    SEARCH = "SEARCH"
    Q_LEARN = "Q_LEARN"
    Q_APPROXIMATE = "Q_APPROXIMATE"

# For Q-Learning Agent
class Learning:
    ALPHA = None
    GAMMA = None
    EPSILON = None
    REWARD = 1
    CALLS_QVALS = "calls_qvals.json"
    PLAY_QVALS = "play_qvals.json"