'''
File for reinforcement learning-based Player classes (Q-Learning and Q-Approximation).
'''

import json
import os
import random
from collections import defaultdict

from players.player import Player
from utils.constants import learning
from utils.constants import CALLS_QVALS
from utils.constants import PLAY_QVALS

'''
An agent which learns Q-Values of (state, action) pairings through experience.
Two sets of Q-Values for making calls and choosing cards
Making calls:
    State definition:
        Number of players left in game
        Number of players remaining to call after the agent
        Ranks of cards in hand
        Sum of calls given so far
    Actions: all possible legal calls
Choosing cards:
    State definition:
        Remaining cards each card in hand is less than
        Number of players to play after the agent
        Sum of calls made by remaining players (ordered by play)
        Sum of wins by remaining players (ordered by play)
        Immediate rank of each card if chosen
        Current calls and wins for the agent
    Actions: playing top card, second card, etc. by rank
'''

class QLearning(Player):

    def __init__(self, name, numLives, history):
        Player.__init__(self, name, numLives, history)
        self.alpha = learning.alpha
        self.gamma = learning.gamma
        self.epsilon = learning.epsilon
        if os.path.exists(name + "_" + CALL_QVALS):
            with open(name + "_" + CALLS_QVALS):
                self.qCalls = json.load(name + "_" + CALLS_QVALS)
        else:
            self.qCalls = defaultdict(float)
        if os.path.exists(name + "_" + PLAY_QVALS):
            with open(name + "_" + PLAY_QVALS):
                self.qPlay = json.load(name + "_" + PLAY_QVALS)
        else:
            self.qPlay = defaultdict(float)

    def makeCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals = {}):
        self.cardRanker = cardRanker
        playersLeft = numPlayers - len(currCalls) - 1
        rankedCards = sorted([self.cardRanker(card) for card in self.currHand])
        calls = sum(currCalls.values())
        state = (numPlayers, playersLeft, rankedCards, calls)
        actions = [i for i in range(len(self.currHand) + 1) if i != illegal]
        if random.random() < self.epsilon:
            return self.currHand.pop(random.choice(actions))
        else:
            topActions = []
            maxVal = float("-inf")
            for action in actions:
                currVal = self.getCallValue(state, action)
                if currVal > maxVal:
                    topActions = [action]
                elif currVal == maxVal:
                    topActions.append(action)
            selected = random.choice(topActions)
            return self.currHand.pop(selected)

    def chooseCard(self, calls, wins, lastHand, power, plays, namedPlays, shown, cardRange):
        currRanks = set([card.rank for card in self.currHand])
        allCards = []
        for num in range(cardRange):
            if num == power:
                continue
            currRank = []
            inHand = []
            for suit in CardInfo.SUITS:
                card = Card(num, suit)
                if card in self.currHand:
                    inHand.append(card)
                currRank.append((card, card in shown))
            allCards.append((currRank, inHand))
        for suit in CardInfo.SUITS:
            powerCard = Card(power, suit)
            if powerCard in self.currHand:
                allCards.append(([(powerCard, powerCard in shown)], [powerCard]))
            else:
                allCards.append(([(powerCard, powerCard in shown)], []))

        count = 0
        # number of cards remaining that each card is less than
        lessThan = {}
        for rank in allCards:
            if rank[1]:
                for card in rank[1]:
                    lessThan[card] = count
            for cardData in rank[0]:
                if cardData[1]:
                    continue
                else:
                    count += 1

        playersLeft = []
        for player in calls:
            if plays[player] is None:
                playersLeft.append(player)

        sumCalls = sum([calls[player] for player in playersLeft])
        sumWins = sum([wins[player] for player in playersLeft])

        currRanks = []

        state = (lessThan, len(playersLeft), sumCalls, sumWins, currRanks, self.currCall, wins[self.name])

    def update(wins):
        if sum(wins) == self.currCall:
            pass
        else:
            pass

    def getCallValue(self, state, action):
        return self.qCalls[(state, action)]

    def getPlayValue(self, state, action):
        return self.qPlays[(lessThan, playersLeft, calls, wins, currRanks, currCall, currWin, action)]

    def saveQVals(self):
        if os.path.exists(name + "_" + CALL_QVALS):
            os.remove(name + "_" + CALL_QVALS)
        with open(name + "_" + CALL_QVALS, "w"):
            json.dump(self.qCalls)
        if os.path.exists(name + "_" + PLAY_QVALS):
            os.remove(name + "_" + PLAY_QVALS)
        with open(name + "_" + PLAY_QVALS, "w"):
            json.dump(self.qPlays)

class QApproximate(Player):
    pass

