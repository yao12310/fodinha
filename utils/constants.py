'''
Util file for constants. (Not for messages)
'''

# Play modes
PLAY = "PLAY"
TRIAL = "TRIAL"

# Game play strings
POWER_YES = "y"
POWER_NO = "n"
CANCELLED = "Cancelled"

# Strategies
EASY = "EASY"
MEDIUM = "MEDIUM"
HARD = "HARD"
RANDOM_FOREST = "RANDOM_FOREST"
NEURAL_NET = "NEURAL_NET"
LOGISTIC = "LOGISTIC"
SEARCH = "SEARCH"
Q_LEARN = "Q_LEARN"
Q_APPROXIMATE = "Q_APPROXIMATE"

# Sleep Time
SLEEP_TIME = 0

# Agent parameters
# Weight, discount, epsilon exploration
learning = {"alpha": None, "gamma": None, "epsilon": None}

# Files for storing Q-Values
CALLS_QVALS = "calls_qvals.json"
PLAY_QVALS = "play_qvals.json"