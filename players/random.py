'''
File for Random player class.
'''

import random
import time

from players.player import Player
from utils.constants import Gameplay
from utils.constants import SLEEP_TIME

'''
An agent which makes all decisions completely randomly among legal options.
Used for benchmarking.
'''
class Random(Player):
    def choosePower(self, cand, shown):
        if random.random() > .5:
            return Gameplay.POWER_YES
        return Gameplay.POWER_NO

    def makeCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals = {}):
        choices = [call for call in range(len(self.currHand) + 1) if call != illegal]
        return random.choice(choices)

    def chooseCard(self, calls, wins, lastHand, power, plays, namedPlays, shown, cardRange):
        rand = random.choice(range(len(self.currHand)))
        choice = self.currHand.pop(rand)
        print("{} played the {}.".format(self.name, str(choice)))
        print()
        time.sleep(SLEEP_TIME)
        return choice
