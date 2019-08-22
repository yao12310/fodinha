'''
File for player type choosing logic.
'''

from players.manual import Manual
from players.search import Search
from players.prob import Easy
from players.prob import Medium
from players.prob import Hard
from players.logistic import Logistic
from players.nn import NeuralNet
from players.reinforcement import QLearning
from players.reinforcement import QApproximate
from utils.constants import *

'''
Method for decision-making: called by Game instance
Makes decisions for player type based on name
'''
def chooseStrategy(name, numLives, history):
    if EASY in name:
        return Easy(name, numLives, history)
    elif MEDIUM in name:
        return Medium(name, numLives, history)
    elif HARD in name:
        return Hard(name, numLives, history)
    elif SEARCH in name:
        return Search(name, numLives, history)
    elif LOGISTIC in name:
        return Logistic(name, numLives, history)
    elif NEURAL_NET in name:
        return NeuralNet(name, numLives, history)
    elif Q_LEARN in name:
        return QLearning(name, numLives, history)
    elif Q_APPROXIMATE in name:
        return QApproximate(name, numLives, history)
    else:
        return Manual(name, numLives, history)