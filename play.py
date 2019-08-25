'''
Core file for launching game of Fodinha.
'''

'''
To-Do List

Implementations:

TODO: General game logic
    >> Done
TODO: Manual player
    >> Done
TODO: Sort hands as players play cards
TODO: Logic for 1-card hand size rounds
    >> Done
TODO: Don't prompt for card index when only one card left
    >> Done
TODO: Logic for stopping Easy AI from making illegal calls
    >> Done
TODO: Logic for Easy AI on one-card hands
    >> Done
TODO: Hard AI: Non-random selection of cards during hands
    >> Done
TODO: Trial mode for playing arbitrary numbers of games
    >> Done
TODO: Logistic AI: general infrastructure for ML AI and model design
TODO: QLearning AI: reinforcement learning approach
    >> Done
TODO: QApproximation AI: RL approach but with linear approximation of Q values
TODO: One-card hand logic for RL agents
TODO: Random play agent for benchmarking
    >> Done

Refactoring:

TODO: Util method for power card choice, requiring a specific kind of input (i.e. only y / n)
    >> Done
TODO: Decide whether to use dictionaries keyed on name in Game or just numerical indices
    >> Decided on numerical indices, only named____ variables use name keys
TODO: Break Game class into Game, Round, and Hand classes
    >> Done
TODO: Have the power card be represented by an int, not the string rank
    >> Done
TODO: Divide player class into abstract class and manual player class
    >> Done
TODO: Pass in illegal call information from round instead of computing in Player
    >> Done
TODO: History class instead of each object housing separate info, pass reference around
TODO: Move different player types into individual files
    >> Done
TODO: Move utils and game play classes into separate directories
    >> Done
TODO: Decide on best inheritance structure for Easy -  Hard AIs
TODO: Refactor counting < and > card counts into a util
TODO: Put constants into static classes
    >> Done

Bug Fixes:

TODO: Fix dealer update logic, perhaps by not modifying names / players and using elim
    >> Done
TODO: Edge case handling for simultaneous loss (negative lives)
    >> Done
TODO: Edge case handling for when the entire hand cancels
    >> Done
TODO: Fix winner not going first in the next hand
    >> Done
TODO: Suits shouldn't matter when ranking in AI (except power) -- preserve O(n)
    >> Done

Misc:

TODO: Doc strings for Player classes
    >> Done
TODO: Show "Cancelled" instead of "None"
    >> Done
TODO: Print dictionaries more cleanly instead of on one line (also, order entries by play)
TODO: Plural vs singular when updating life counts
TODO: README with rules and project overview
    >> Done
TODO: Exception for non-implemented player classes
TODO: Correct standings past first place at end of game
    >> Done
TODO: Math details in README
'''

import sys
from random import shuffle
from numpy import mean

from logic.game import Game
from utils.constants import Modes

mode = sys.argv[1]
if mode == Modes.PLAY:
    cardRange = int(sys.argv[2])
    numLives = int(sys.argv[3])
    powerTries = int(sys.argv[4])
    names = sys.argv[5:]
    game = Game(names, cardRange, numLives, powerTries)
    game.playGame()
elif mode == Modes.TRIAL:
    numTrials = int(sys.argv[2])
    writeStep = int(sys.argv[3])
    writeFile = sys.argv[4]
    cardRange = int(sys.argv[5])
    numLives = int(sys.argv[6])
    powerTries = int(sys.argv[7])
    names = sys.argv[8:]
    wins = {name: 0 for name in names}
    finishes = {name: [] for name in names}
    for i in range(numTrials):
        if i != 0 and i % writeStep == 0:
            with open("count.txt", "a") as f:
                f.write("Iteration: {}\n Wins by Player: {}\n Average Finish (last {}): {}\n"
                    .format(i, wins, writeStep, {name: mean(stand[-writeStep:]) for (name, stand) in finishes.items()}))
        shuffle(names)
        game = Game(names.copy(), cardRange, numLives, powerTries)
        try:
            game.playGame()
            standings = game.standings
            wins[standings[0]] += 1
            curr = 1
            for stand in standings:
                finishes[stand].append(curr)
                curr += 1
        except Exception as e:
            with open("count.txt", "a") as f:
                f.write("Iteration {}: {}".format(i, e))
    print("Trials: {}".format(numTrials))
    print("Wins by player: {}".format(wins))
    print("Average finish by player: {}".format({name: mean(stand) for (name, stand) in finishes.items()}))
else:
    print("Invalid game mode selected!")
