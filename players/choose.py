from players.manual import Manual
from players.search import Search
from players.prob import Easy
from players.prob import Medium
from players.prob import Hard
from players.softmax import Softmax
from players.nn import NeuralNet
from players.rf import RandomForest
from utils.constants import *

def chooseStrategy(name, numLives, history):
    if EASY in name:
        return Easy(name, numLives, history)
    elif MEDIUM in name:
        return Medium(name, numLives, history)
    elif HARD in name:
        return Hard(name, numLives, history)
    elif SEARCH in name:
        return Search(name, numLives, history)
    elif SOFTMAX in name:
        return Softmax(name, numLives, history)
    elif NEURAL_NET in name:
        return NeuralNet(name, numLives, history)
    elif RANDOM_FOREST in name:
        return RandomForest(name, numLives, history)
    else:
        return Manual(name, numLives, history)