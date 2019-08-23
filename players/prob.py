'''
File for expected utility-based Player classes (Easy, Medium, Hard).
'''

import time

import scipy.stats as sc
from players.player import Player
from utils.card import Card
from utils.card import CardInfo
from utils.card import CardUtils
from utils.constants import SLEEP_TIME
from utils.constants import Gameplay

'''
Class for Easy AI player (expected utility).
Implements round-level decisions via the following logic:
    Choosing power card: Default to showing 3 cards, unless candidate has been shown
    Make call:
        Assumes uniform distribution of cards across other hands and random play
        Does not update according to other information and ignores cancellation
        Makes calls per card depending on probability of victory
        Math: X ~ hypergeometric(g + l, l, p - 1), where:
            X is RV representing # cards played each hand > card in hand
            g, l are # cards the card is greater than and less than among all remaining cards
            p is the total number of players
            P(X = 0) is the expected value of indicator for winning with the card
            Since loss is symmetric, call when P(X = 0) > 1/2
    Choose card:
        Random
'''
class Easy(Player):

    def choosePower(self, cand, shown):
        if cand in shown:
            return Gameplay.POWER_YES
        return Gameplay.POWER_NO

    def makeCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals = {}):
        # at beginning of each round, store the card ranker for the current round
        self.cardRanker = cardRanker
        if namedDeals:
            return self.makeOneCardCall(currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals)

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
        # number of cards remaining that each card is greater than
        greatThan = {}
        for rank in allCards:
            if rank[1]:
                for card in rank[1]:
                    greatThan[card] = count
            for cardData in rank[0]:
                if cardData[1]:
                    continue
                else:
                    count += 1

        count = 0
        # number of cards remaining that each card is less than
        lessThan = {}
        for rank in allCards[::-1]:
            if rank[1]:
                for card in rank[1]:
                    lessThan[card] = count
            for cardData in rank[0]:
                if cardData[1]:
                    continue
                else:
                    count += 1

        call = 0
        total = 0
        for card in self.currHand:
            great = greatThan[card]
            less = lessThan[card]
            hypergeom = sc.hypergeom(great + less, less, numPlayers - 1)
            prob = hypergeom.pmf(0)
            if prob > .5:
                call += 1
            total += prob
        average = total / roundNum

        # if call would be illegal, average probability informs + or -
        # unless call would be over the total, in which case go down
        # or if call would be negative, in which case go up
        if call == illegal:
            if call == roundNum:
                call -= 1
            elif call == 0:
                call += 1
            else:
                call = call + (average > .5) - (average <= .5)

        self.currCall = call
        self.calls.append(call)

        return call

    def makeOneCardCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals = {}):
        if illegal == 0 or illegal == 1:
            self.currCall = 1 - illegal
            self.calls.append(1 - illegal)
            return 1 - illegal
        dealtCards = list([card for (name, card) in namedDeals.items() if name != self.name])
        cardsSet = set(dealtCards)
        topCard = dealtCards[dealtCards.index(max(dealtCards, key = self.cardRanker))]
        topRank = self.cardRanker(topCard)
        total = 0
        greater = 0
        for num in range(cardRange):
            for suit in CardInfo.SUITS:
                card = Card(num, suit)
                if card in shown:
                    continue
                if card in cardsSet:
                    continue
                if self.cardRanker(card) > topRank:
                    greater += 1
                total += 1
        call = 1 * (greater / total > .5)

        self.currCall = call
        self.calls.append(call)

        return call

    def chooseCard(self, calls, wins, lastHand, power, plays, namedPlays, shown, cardRange):
        rand = sc.randint(0, len(self.currHand)).rvs()
        choice = self.currHand.pop(rand)
        print("{} played the {}.".format(self.name, str(choice)))
        print()
        time.sleep(SLEEP_TIME)
        return choice

'''
Class for Hard AI player (expected utility).
Implements round-level decisions via the following logic:
    Choosing power card: Same as Easy
    Make call: Same as Easy
    Choose card:
        Assumes randomness in play from other players
        Caches probability of wins computed during call making to rank cards
        Updates probability of a win for each card whenever turn to select:
            Computes both probability of a win for the current hand and future hands
            Tracks cards shown through course of play during the round and current hand
            Considers whether cards already played this hand can win and players coming after
        Check expected value of wins for playing each card, take card which gets closest to call
'''
class Hard(Player):

    def choosePower(self, cand, shown):
        if cand in shown:
            return Gameplay.POWER_YES
        return Gameplay.POWER_NO

    def makeCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals = {}):
        return Easy.makeCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals)    

    def makeOneCardCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals = {}):
        return Easy.makeOneCardCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals)

    def chooseCard(self, calls, wins, lastHand, power, plays, namedPlays, shown, cardRange):
        allCards = []
        for num in range(cardRange):
            if num == power:
                continue
            for suit in CardInfo.SUITS:
                card = Card(num, suit)
                allCards.append((card, card in self.currHand, card in shown))
        for suit in CardInfo.SUITS:
            powerCard = Card(power, suit)
            allCards.append((powerCard, powerCard in self.currHand, powerCard in shown))

        count = 0
        # number of cards remaining that each card is greater than
        greatThan = {}
        for cardData in allCards:
            if cardData[1]:
                greatThan[cardData[0]] = count
            elif cardData[2]:
                continue
            else:
                count += 1

        count = 0
        # number of cards remaining that each card is less than
        lessThan = {}
        for cardData in allCards[::-1]:
            if cardData[1]:
                lessThan[cardData[0]] = count
            elif cardData[2]:
                continue
            else:
                count += 1

        # find probability of winning the current hand and for a future hand
        currProbs = []
        genProbs = []
        after = len(calls) - len([play for play in plays if play != None])
        for i in range(len(self.currHand)):
            card = self.currHand.get(i)
            feasible = True
            cardRank = self.cardRanker(card)
            for play in plays:
                if self.cardRanker(play) >= cardRank:
                    feasible = False
                    break
            great = greatThan[card]
            less = lessThan[card]
            if feasible:
                if not after:
                    currProbs.append(1)
                else:
                    currProbs.append(sc.hypergeom(great + less, less, after).pmf(0))
            else:
                currProbs.append(0)
            genProbs.append(sc.hypergeom(great + less, less, len(calls) - 1).pmf(0))

        # compute sum of current wins additional expected wins given each possible play
        currWin = wins[self.name]
        expected = []
        for i in range(len(self.currHand)):
            curr = currProbs[i]
            for j in range(len(self.currHand)):
                if j == i:
                    continue
                curr += genProbs[j]
            expected.append(currWin + curr)

        # take the choice whose play this turn minimizes expected distance between wins and call
        choiceIndex = expected.index(min(expected, key = lambda e: abs(e - self.currCall)))
        choice = self.currHand.pop(choiceIndex)
        print("{} played the {}.".format(self.name, str(choice)))
        print()
        time.sleep(SLEEP_TIME)
        return choice
