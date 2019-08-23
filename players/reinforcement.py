'''
File for reinforcement learning-based Player classes (Q-Learning and Q-Approximation).
'''

import pickle
import os
import random
from collections import defaultdict

from players.player import Player
from utils.constants import Learning
from utils.constants import Gameplay
from utils.card import Card
from utils.card import CardInfo

'''
An agent which learns Q-Values of (state, action) pairings through experience.
Two sets of Q-Values for making calls and choosing cards
Making calls:
    State definition:
        Number of players remaining to call after the agent
        Ranks of cards in hand
        Sum of calls given so far
        Hand size
    Actions: all possible legal calls
Choosing cards:
    State definition:
        Remaining cards each card in hand is less than (rounded to nearest 5)
            See constants.py for option to only take the top card's lessThan number
        Number of players to play after the agent
        Sum of call-win differences for remaining players (ordered by play)
        Immediate ranks of each card if played
            See constants.py for option to just use index of lowest rank card that would be current top card
        Current calls and wins for the agent
    Actions: playing top card, second card, etc. by rank
'''

class QLearning(Player):

    def __init__(self, name, numLives, history):
        Player.__init__(self, name, numLives, history)
        self.alpha = Learning.ALPHA
        self.gamma = Learning.GAMMA
        self.epsilon = Learning.EPSILON
        if os.path.exists(Learning.Q_DIREC + name + "_" + Learning.CALLS_QVALS):
            with open(Learning.Q_DIREC + name + "_" + Learning.CALLS_QVALS, "rb") as file:
                self.qCalls = pickle.load(file)
        else:
            self.qCalls = defaultdict(float)
            self.qCalls[Learning.DECAY] = 1.0
        if os.path.exists(Learning.Q_DIREC + name + "_" + Learning.PLAY_QVALS):
            with open(Learning.Q_DIREC + name + "_" + Learning.PLAY_QVALS, "rb") as file:
                self.qPlays = pickle.load(file)
        else:
            self.qPlays = defaultdict(float)
            self.qPlays[Learning.DECAY] = 1.0

    def choosePower(self, cand, shown):
        if cand in shown:
            return Gameplay.POWER_YES
        return Gameplay.POWER_NO

    def makeCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals = {}):
        self.cardRanker = cardRanker
        playersLeft = numPlayers - len(currCalls) - 1
        rankedCards = tuple(sorted([self.cardRanker(card) for card in self.currHand]))
        calls = sum(currCalls.values())
        state = (playersLeft, rankedCards, calls, len(self.currHand))
        actions = [i for i in range(len(self.currHand) + 1) if i != illegal]
        if random.random() < self.epsilon / self.qCalls[Learning.DECAY]:
            action = random.choice(actions)
        else:
            topActions = []
            maxVal = float("-inf")
            for action in actions:
                currVal = self.getCallValue(state, action)
                if currVal > maxVal:
                    topActions = [action]
                elif currVal == maxVal:
                    topActions.append(action)
            action = random.choice(topActions)
        self.callCache = (state, action)
        self.playCache = []

        self.currCall = action
        self.calls.append(action)

        return action

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
        lessThan = []
        for rank in allCards:
            if rank[1]:
                for card in rank[1]:
                    lessThan.append(5 * round(count / 5))
            for cardData in rank[0]:
                if cardData[1]:
                    continue
                else:
                    count += 1

        # to save space, flag for only using the lessThan number for the top card in hand
        if not Learning.ALL_LESS:
            lessThan = lessThan[-1]

        playersLeft = []
        for player in calls:
            if namedPlays[player] is None:
                playersLeft.append(player)

        sumDiffs = sum([calls[player] for player in playersLeft]) - sum([wins[player] for player in playersLeft])

        # either compute immediate ranks for each card if played
        if Learning.USE_RANKS:
            # get ranking of cards if they were played now (ranked with 0 as the top)
            rankedPlays = sorted([self.cardRanker(play) for play in plays])
            rankedHand = sorted([self.cardRanker(card) for card in self.currHand])
            currRanks = []
            playIndex = 0
            handIndex = 0
            while playIndex < len(plays) and handIndex < len(self.currHand):
                if rankedHand[handIndex] > rankedPlays[playIndex]:
                    playIndex += 1
                elif rankedHand[handIndex] < rankedPlays[playIndex]:
                    currRanks.append(len(plays) - playIndex)
                    handIndex += 1
                else:
                    currRanks.append(float("inf"))
                    handIndex += 1
            # if the playIndex passed the end, then the remaining cards would all be top cards
            # note that 0 as top card here is not standard, zeroeth index typically refers
            # to the lowest card in the context of sorted cards
            if playIndex == len(plays):
                currRanks += [0] * (len(self.currHand) - len(currRanks))
            state = (lessThan, len(playersLeft), sumDiffs, currRanks, self.currCall, wins[self.name])
        # or check the lowest card that would immediately be first if played
        else:
            topRank = self.cardRanker(max(plays, key = self.cardRanker))
            wouldWin = -1
            rankedHand = sorted([self.cardRanker(card) for card in self.currHand])
            for i in range(len(self.currHand)):
                if rankedHand[i] > topRank:
                    wouldWin = i
                    break
            state = (lessThan, len(playersLeft), sumDiffs, wouldWin, self.currCall, wins[self.name])

        actions = range(len(self.currHand))
        self.currHand = sorted(self.currHand, key = self.cardRanker)
        if random.random() < self.epsilon / self.qPlays[Learning.DECAY]:
            action = random.choice(actions)
        else:
            topActions = []
            maxVal = float("-inf")
            for action in actions:
                currVal = self.getPlayValue(state, action)
                if currVal > maxVal:
                    topActions = [action]
                elif currVal == maxVal:
                    topActions.append(action)
            action = random.choice(topActions)
        self.playCache.append((state, action))
        return self.currHand.pop(action)

    def update(self, wins):
        self.qCalls[Learning.DECAY] += Learning.DECAY_INCREMENT * 10
        self.qPlays[Learning.DECAY] += Learning.DECAY_INCREMENT
        # if no lives are lost in the round, then default reward for all actions
        if sum(wins) == self.currCall:
            self.qCalls[self.callCache] = ((1 - self.alpha) * self.qCalls[self.callCache] + self.alpha * Learning.REWARD)
            for pair in self.playCache:
                self.qPlays[pair] = ((1 - self.alpha) * self.qPlays[pair] + self.alpha * Learning.REWARD)
        # else use the following scheme for rewards
        # give the calls action reward equal to the negative of the number of lives lost
        # give the actual number of wins default reward
        # if too many hands won, then for all the hands that were won (unless the lowest card was chosen),
        # penalize the chosen action by the # lives lost and reward all actions that played lower cards
        # vice versa if too many hands lost
        else:
            livesLost = abs(sum(wins) - self.currCall)
            self.qCalls[self.callCache] = ((1 - self.alpha) * self.qCalls[self.callCache] - self.alpha * livesLost)
            self.qCalls[(self.callCache[0], sum(wins))] = ((1 - self.alpha) * 
                self.qCalls[(self.callCache[0], sum(wins))] + self.alpha * Learning.REWARD)
            handSize = self.callCache[0][3]
            if sum(wins) > self.currCall:
                for i in range(len(wins)):
                    if not wins[i]:
                        continue
                    pair = self.playCache[i]
                    # retrieve the number of options the agent had
                    numOptions = handSize - i
                    # if the agent chose the lowest card in hand and still won, then 
                    # nothing could be done (could have been faulty call, which is penalized)
                    if pair[1] == 0:
                        continue
                    self.qPlays[pair] = ((1 - self.alpha) * self.qPlays[pair] - self.alpha * livesLost)
                    for j in range(numOptions):
                        # reward all options which played lower cards than the chosen
                        if j >= pair[1]:
                            continue
                        self.qPlays[(pair[0], j)] = ((1 - self.alpha) * self.qPlays[(pair[0], j)] + self.alpha * Learning.REWARD)
            else:
                for i in range(len(wins)):
                    if wins[i]:
                        continue
                    pair = self.playCache[i]
                    # retrieve the number of options the agent had from the first element
                    # of state, which always contains the lessThan tuple
                    numOptions = handSize - i
                    # if the agent chose the highest card in hand and still won, then
                    # nothing could be done (could have been faulty call, which is penalized)
                    if pair[1] == numOptions - 1:
                        continue
                    self.qPlays[pair] = ((1 - self.alpha) * self.qPlays[pair] - self.alpha * livesLost)
                    for j in range(numOptions):
                        # reward all options which played higher cards than the chosen
                        if j <= pair[1]:
                            continue
                        self.qPlays[(pair[0], j)] = ((1 - self.alpha) * self.qPlays[(pair[0], j)] + self.alpha * Learning.REWARD)


    def getCallValue(self, state, action):
        return self.qCalls[(state, action)]

    def getPlayValue(self, state, action):
        return self.qPlays[(state, action)]

    def saveQVals(self):
        if os.path.exists(Learning.Q_DIREC + self.name + "_" + Learning.CALLS_QVALS):
            os.remove(Learning.Q_DIREC + self.name + "_" + Learning.CALLS_QVALS)
        with open(Learning.Q_DIREC + self.name + "_" + Learning.CALLS_QVALS, "wb") as file:
            pickle.dump(self.qCalls, file)
        if os.path.exists(Learning.Q_DIREC + self.name + "_" + Learning.PLAY_QVALS):
            os.remove(Learning.Q_DIREC + self.name + "_" + Learning.PLAY_QVALS)
        with open(Learning.Q_DIREC + self.name + "_" + Learning.PLAY_QVALS, "wb") as file:
            pickle.dump(self.qPlays, file)

class QApproximate(Player):
    pass

