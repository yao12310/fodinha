'''
File for reinforcement learning-based Player classes (Q-Learning and Q-Approximation).
'''

import pickle
import os
import numpy as np
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

'''
An agent which approximates Q-Values of (state, action) pairings through experience.
Inherits various generic methods from QLearning agent, but updates differently and different states.
Learns weights for linear functions that approximate Q-Values.
Two categories of weights, with multiple sets of weights and features in each for different hand sizes.
Call Making (n-card hand):
    State is given by shown cards, hand, number of players, sum of calls so far, and number of calls so far

    Q(s,a) should be high if s has high cards in hand and a is a high call, or vice versa
    f_i(s,a), 1 <= i <= n: h_i * a, where h_i is the normalized rank of the ith ranked card in hand
    (normalized against all remaining cards in the game) and a is the value of the call centered
    centered against other calls. Intuition: positive if h_i and a are both below 
    average or above average, else negative.

    May also be desirable to make high calls if the current sum is low (or low calls in the other case). 
    Hence, g(s,a): a * (p * avg - calls), where a is the same, calls is the sum of calls so far, 
    p is the number of calls so far, avg is the hand size / total num of players.

    Transitions to a card choosing pseudo-state whose value is determined by averaging over
    the different possibilities for win-call differences and number of players to play after the agent.
    
Card Choosing (n-card hand):
    State is given by shown cards, hand, sum of win-call differences among players after, current call, 
    current wins, number of players to play after the agent, plays so far, and number of players.

    Q(s,a) should be high if an above average card is played when the agent is short on wins (and vice
    versa). This effect should be amplified if the sum of win-call diffs is positive, indicating that
    players after won't be going for the win as well, as well as when fewer players are to play (giving
    higher certainty).
    r_i(s,a): normalized ranks of the ith ranked card in hand normalized against all remaining cards
    w_j(s,a): whether the jth ranked card in hand is higher than all other cards played so far
    f(s,a): a * (call - wins), which is positive if a is above average and more wins are needed, and vice versa
    g(s,a): a * sumdiffs, which is positive if a is above average and players after don't need more wins, and vice versa
    h(s,a): absolute value of the action centered on the indices in hand
    multiplied by the centered number of players who've played already since extreme plays when more
    players have played is desirable, as are moderate plays when fewer players have played

    Transitions to a card choosing pseudo-state (unless it was the last card in hand, which leads to the terminal
    state) whose value is determined by averaging over different possibilities for number of players to play after.
'''
class QApproximate(QLearning):

    def makeCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals = {}):
        self.cardRanker = cardRanker
        handSize = len(self.currHand)
        state = (shown, self.currHand.copy(), numPlayers, sum(currCalls.values()), len(currCalls))
        actions = [i for i in range(len(self.currHand) + 1) if i != illegal]
        if random.random() < self.epsilon / self.qCalls[Learning.DECAY]:
            action = random.choice(actions)
            # even if a random action is made, need to cache for update step
            _, cache = self.getCallValue(state, action, handSize, cardRange)
        else:
            topActions = []
            maxVal = float("-inf")
            for action in actions:
                currVal, cache = self.getCallValue(state, action, handSize, cardRange)
                if currVal > maxVal:
                    topActions = [(action, cache)]
                elif currVal == maxVal:
                    topActions.append((action, cache))
            action, cache = random.choice(topActions)

        self.callCache = cache
        self.playCache = []

        self.currCall = action
        self.calls.append(action)

        return action

    def getCallValue(self, state, action, handSize, cardRange):
        weights = self.qCalls[handSize]
        # float only by default settings, change to array
        if type(weights) == float:
            weights = np.array([np.random.rand() for _ in range(handSize + 1)])
            self.qCalls[handSize] = weights

        features = []

        # f_i(s,a) computation
        centAction = action - handSize / 2

        allCards = []
        shown = state[0]
        currHand = state[1]
        for num in range(cardRange):
            for suit in CardInfo.SUITS:
                card = Card(num, suit)
                if card in currHand or card in shown:
                    continue
                allCards.append(card)

        rankedCards = list(map(self.cardRanker, allCards))
        avgRank = np.mean(rankedCards)
        sdRank = np.sqrt(np.var(rankedCards))
        normHand = [(self.cardRanker(card) - avgRank) / sdRank for card in currHand]

        features.extend([centAction * rank for rank in normHand])

        # g(s,a) computation
        numPlayers = state[2]
        calls = state[3]
        played = state[4]
        features.append(centAction * (handSize / numPlayers * played - calls))
        features = np.array(features)
        qVal = np.dot(weights, features)

        cache = (handSize, features, qVal, state, action, cardRange, allCards)

        return qVal, cache

    def chooseCard(self, calls, wins, lastHand, power, plays, namedPlays, shown, cardRange):
        handSize = len(self.currHand)

        playersLeft = []
        for player in calls:
            if namedPlays[player] is None:
                playersLeft.append(player)

        sumDiffs = sum([calls[player] for player in playersLeft]) - sum([wins[player] for player in playersLeft])
        state = (shown, self.currHand.copy(), sumDiffs, self.currCall, wins[self.name], len(playersLeft), plays, len(calls))
        actions = range(len(self.currHand))
        if random.random() < self.epsilon / self.qCalls[Learning.DECAY]:
            action = random.choice(actions)
            # even if a random action is made, need to cache for update step
            _, cache = self.getPlayValue(state, action, handSize, cardRange)
        else:
            topActions = []
            maxVal = float("-inf")
            for action in actions:
                currVal, cache = self.getPlayValue(state, action, handSize, cardRange)
                if currVal > maxVal:
                    topActions = [(action, cache)]
                elif currVal == maxVal:
                    topActions.append((action, cache))
                else:
                    raise SystemExit
            action, cache = random.choice(topActions)
            self.playCache.append(cache)
        return self.currHand.pop(action)

    def getPlayValue(self, state, action, handSize, cardRange):
        weights = self.qPlays[handSize]
        # float only by default settings, change to array
        if type(weights) == float:
            weights = np.array([np.random.rand() for _ in range(2 * handSize + 3)])
            self.qPlays[handSize] = weights

        features = []

        # r_i(s,a) computation
        allCards = []
        shown = state[0]
        currHand = state[1]
        for num in range(cardRange):
            for suit in CardInfo.SUITS:
                card = Card(num, suit)
                if card in currHand or card in shown:
                    continue
                allCards.append(Card(num, suit))

        rankedCards = list(map(self.cardRanker, allCards))
        avgRank = np.mean(rankedCards)
        sdRank = np.sqrt(np.var(rankedCards))
        normHand = [(self.cardRanker(card) - avgRank) / sdRank for card in currHand]

        features.extend(normHand)

        # w_j(s,a) computation
        plays = state[6]
        topRank = self.cardRanker(max(plays, key = self.cardRanker))
        features.extend([int(self.cardRanker(card) > topRank) for card in currHand])

        # f(s,a) computation
        calls = state[3]
        wins = state[4]
        avgIndex = (handSize - 1) / 2
        centAction = action - avgIndex
        features.append(centAction * (calls - wins))

        # g(s,a) computation
        sumDiffs = state[2]
        features.append(centAction * sumDiffs)

        # h(s,a) computation
        numPlayers = state[7]
        numPlays = numPlayers - state[5] - 1
        features.append(abs(centAction) * (numPlays - (numPlayers - 1) / 2))

        features = np.array(features)
        qVal = np.dot(weights, features)

        cache = (handSize, features, qVal, state, action, cardRange, allCards)

        return qVal, cache

    def update(self, wins):
        self.qCalls[Learning.DECAY] += Learning.DECAY_INCREMENT * 10
        self.qPlays[Learning.DECAY] += Learning.DECAY_INCREMENT
        # if no lives are lost in the round, then default reward for all actions
        finalDiff = self.currCall - sum(wins)
        # if call matched wins, give every action the default reward
        if not finalDiff:
            reward = Learning.REWARD
        else:
            reward = -abs(finalDiff)

        # update call weights
        handSize = self.callCache[0]
        features = self.callCache[1]
        qVal = self.callCache[2]
        state = self.callCache[3]
        action = self.callCache[4]
        cardRange = self.callCache[5]
        remainCards = self.callCache[6]

        callWeights = self.qCalls[handSize]
        # find expected value from the next state (averaging over possible
        # number of calls and players to play after on the first hand)
        nextStateQ = []
        if not state[3]:
            nextStateQ.append(0)
        else:
            for calls in range(state[3]):
                for playAfter in range(state[2]):
                    possiblePlays = list(np.random.choice(remainCards, state[2] - playAfter - 1)) + [None] * (playAfter + 1)
                    possibleState = (state[0], state[1], calls, self.currCall, 0, playAfter, possiblePlays, state[2])
                    for possibleAction in range(handSize):
                        nextStateQ.append(self.getPlayValue(possibleState, possibleAction, handSize, cardRange)[0])
        avgNextQ = np.nan_to_num(np.mean(nextStateQ))
        diff = reward + self.gamma * avgNextQ - qVal

        print(diff)
        print(reward + self.gamma * avgNextQ)
        print(qVal)
        print(avgNextQ)
        for i in range(handSize + 1):
            callWeights[i] += self.alpha * diff * features[i]
            print(i, features[i])

        # update play weights
        for cacheIndex in range(len(self.playCache)):
            # in the case where lives were lost in this round:
            # if won too many hands but lost this hand or
            # if won too few hands but won this hand, then no penalty
            if finalDiff > 0 and wins[cacheIndex] or finalDiff < 0 and not wins[cacheIndex]:
                continue
            cache = self.playCache[cacheIndex]
            handSize = cache[0]
            features = cache[1]
            qVal = cache[2]
            state = cache[3]
            action = cache[4]
            cardRange = cache[5]
            remainCards = cache[6]

            playWeights = self.qPlays[handSize]
            # find expected value from the next state (averaging over different
            # possibilities for number of players to play after)
            if handSize == 1:
                nextStateQ = [0]
            else:
                nextStateQ = []
                for playAfter in range(state[7]):
                    possiblePlays = list(np.random.choice(remainCards, state[7] - playAfter - 1)) + [None] * (playAfter + 1)
                    possibleState = (state[0], state[1], state[2] + .5, state[3], 
                        state[4] + 1 / state[7], playAfter, possiblePlays, state[7]
                    )
                    for possibleAction in range(handSize - 1):
                        nextStateQ.append(self.getPlayValue(possibleState, possibleAction, handSize, cardRange)[0])
                avgNextQ = np.mean(nextStateQ)
                diff = reward + self.gamma * avgNextQ - qVal
                for i in range(2 * handSize + 3):
                    playWeights[i] += self.alpha * diff * features[i]
