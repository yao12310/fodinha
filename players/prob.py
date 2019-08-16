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
from utils.constants import POWER_YES
from utils.constants import POWER_NO

'''
Class for simple AI player (expected utility).
Implements round-level decisions via the following logic:
    Choosing power card: Default to showing 3 cards, unless candidate has been shown
    Make call:
        Assumes uniform distribution of cards across other hands and random play
        Does not update according to other information and ignores cancellation
        Computes expected value of wins based on cards in hand
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
            return POWER_YES
        return POWER_NO

    def makeCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, namedDeals = {}):
        if namedDeals:
            return self.makeOneCardCall(currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, namedDeals)

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

        call = 0
        total = 0
        for card in self.currHand:
            great = greatThan[card]
            less = lessThan[card]
            hypergeom = sc.hypergeom(great + less, less, numPlayers - 1)
            prob = hypergeom.pmf(0)
            print(card, prob, great, less)
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

        return call

    def makeOneCardCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, namedDeals = {}):
        if illegal == 0 or illegal == 1:
            return 1 - illegal
        dealtCards = list([card for (name, card) in namedDeals.items() if name != self.name])
        cardsSet = set(dealtCards)
        cardRanker = CardUtils.cardRankerGen(power, cardRange)
        topCard = dealtCards[dealtCards.index(max(dealtCards, key = cardRanker))]
        topRank = cardRanker(topCard)
        total = 0
        greater = 0
        for num in range(cardRange):
            for suit in CardInfo.SUITS:
                card = Card(num, suit)
                if card in shown:
                    continue
                if card in cardsSet:
                    continue
                if cardRanker(card) > topRank:
                    greater += 1
                total += 1
        print([str(card) for card in dealtCards], greater / total)
        call = 1 * (greater / total > .5)
        return call

    def chooseCard(self, calls, wins, lastHand, power, plays):
        rand = sc.randint(0, len(self.currHand)).rvs()
        choice = self.currHand.pop(rand)
        print("{} played the {}.".format(self.name, str(choice)))
        print()
        time.sleep(SLEEP_TIME)
        return choice

class Medium(Player):

    def choosePower(self, cand, shown):
        if cand in shown:
            return POWER_YES
        return POWER_NO

class Hard(Player):

	pass