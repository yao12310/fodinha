'''
File for player type choosing logic.
'''

from players.manual import Manual
from players.random import Random
from players.search import Search
from players.prob import Easy
from players.prob import Hard
from players.logistic import Logistic
from players.nn import NeuralNet
from players.reinforcement import QLearning
from players.reinforcement import QApproximate
from utils.constants import Strategies

'''
Method for decision-making: called by Game instance
Makes decisions for player type based on name
'''
def chooseStrategy(name, numLives, history):
    if Strategies.RANDOM in name:
        return Random(name, numLives, history)
    elif Strategies.EASY in name:
        return Easy(name, numLives, history)
    elif Strategies.HARD in name:
        return Hard(name, numLives, history)
    elif Strategies.SEARCH in name:
        return Search(name, numLives, history)
    elif Strategies.LOGISTIC in name:
        return Logistic(name, numLives, history)
    elif Strategies.NEURAL_NET in name:
        return NeuralNet(name, numLives, history)
    elif Strategies.Q_LEARN in name:
        return QLearning(name, numLives, history)
    elif Strategies.Q_APPROXIMATE in name:
        return QApproximate(name, numLives, history)
    else:
        return Manual(name, numLives, history)