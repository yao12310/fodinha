'''
File for Round class.
'''
import time

from logic.hand import Hand
from players.player import Player
from utils.card import CardInfo
from utils.card import CardCollection
from utils.card import CardUtils
from utils.constants import *

'''
Round stores round-level information:
    Game info and meta round settings passed down from game.py:
        List of names and Player objects, range of cards, deck
        Dealer, number of cards to be dealt
    Round state:
        Current power card, calls, wins, first player
    Round history: Hands played, cards shown so far
Functionalities:
    Round set-up: shuffle and deal cards, power card, calls
    Launches Hand instances (passes down name, players, calls, wins, power card)
    Computes final differentials (passes back up to Game)
'''
class Round:

    def __init__(self, numCards, dealer, names, players, deck, cardRange, powerTries):
        self.numCards = numCards
        self.dealer = dealer
        self.names = names
        self.players = players
        self.deck = deck
        self.cardRange = cardRange
        self.powerTries = powerTries
        self.numPlayers = len(names)

    def playRound(self):
        self.wins = [0] * self.numPlayers
        self.diffs = [None] * self.numPlayers
        self.hands = []
        orderedWins = []

        # Shuffle and deal cards, recover remaining cards in deck
        # If one card hand, also recover the deals to use for making calls
        remaining, namedDeals = self.dealCards(oneCard = (self.numCards == 1))

        # Prompt dealer for power card
        self.power, self.shown = self.choosePower(remaining, self.players[self.dealer])
        self.cardRanker = CardUtils.cardRankerGen(self.power, self.cardRange)

        # Request calls
        self.calls = self.requestCalls(namedDeals)

        # Play hands
        first = (self.dealer + 1) % self.numPlayers
        winCarry = 0

        for i in range(self.numCards):
            print("Playing hand {} out of {} in this round. Going first is {}.".format(i + 1, self.numCards, self.names[first]))
            if winCarry:
                print("{} wins have carried over. This hand will count for {} wins.".format(winCarry, winCarry + 1))
            lastHand = (i == self.numCards - 1)
            if lastHand:
                print("Last hand of the round! Will force plays from hand, no selection.")
            winner = self.startHand(first, lastHand)
            if winner is None:
                winCarry += 1
            else:
                first = winner
                self.wins[winner] += 1 + winCarry
                orderedWins.append(winner)
                winCarry = 0
            print()
            time.sleep(SLEEP_TIME)

        print("Round of {} cards has concluded!".format(self.numCards))
        print("Original calls were {}".format({self.names[i]: self.calls[i] for i in range(self.numPlayers)}))
        print("Wins turned out to be {}".format({self.names[i]: self.wins[i] for i in range(self.numPlayers)}))
        print("Hands were {}".format({self.names[i]: str(self.players[i].hands[-1]) for i in range(self.numPlayers)}))
        time.sleep(SLEEP_TIME)

        for i in range(self.numPlayers):
            self.diffs[i] = abs(self.calls[i] - self.wins[i])
            if Q_LEARN in self.players[i].name:
                self.players[i].update([winner == i for winner in orderedWins])

    def dealCards(self, oneCard):
        print("Dealing cards...")
        if oneCard:
            namedDeals = {}
        self.deck.shuffle()
        hands = self.deck.deal(self.numCards, self.numPlayers)
        for i in range(self.numPlayers):
            curr = ((self.dealer + 1) + i) % self.numPlayers
            self.players[curr].setHand(hands[curr])
            if oneCard:
                namedDeals[self.names[curr]] = hands[curr].get(0)
        remaining = self.deck.slice(self.numPlayers * self.numCards, None)
        print()
        time.sleep(SLEEP_TIME)
        if oneCard:
            return remaining, namedDeals
        return remaining, {}

    def choosePower(self, remaining, player):
        print("Selecting power card...")
        shown = CardCollection(cards = [])

        for i in range(self.powerTries):
            draw = remaining.get(i)
            print("The draw is the {}.".format(draw))
            cand = (draw.num + 1) % self.cardRange
            namedCand = CardInfo.RANKS[cand]

            if i == self.powerTries - 1:
                print("{} has been forced as the power card!".format(namedCand))
                shown.append(draw)
                print()
                time.sleep(SLEEP_TIME)
                return (cand, shown)

            decision = player.choosePower(cand, shown)

            if decision == POWER_YES:
                print("{} has been chosen as the power card!".format(namedCand))
                shown.append(draw)
                print()
                time.sleep(SLEEP_TIME)
                return (cand, shown)
            if decision == POWER_NO:
                print("{} has rejected {} as the power card.".format(player.name, namedCand))
                shown.append(draw)
                
    def requestCalls(self, namedDeals = {}):
        print("Time to make calls!")
        if namedDeals:
            print("This is a one card hand! You will be able to see all cards except your own.")
        calls = [None] * self.numPlayers
        namedCalls = {}

        for i in range(self.numPlayers):
            curr = ((self.dealer + 1) + i) % self.numPlayers
            name = self.names[curr]
            if curr == self.dealer:
                illegal = self.numCards - sum(namedCalls.values())
            else:
                illegal = -1

            print("It is currently {}'s turn to make a call.".format(name))
            calls[curr] = self.players[curr].makeCall(
                namedCalls, self.numPlayers, self.numCards, self.power, 
                self.shown, illegal, self.cardRange, self.cardRanker, namedDeals
            )
            namedCalls[self.names[curr]] = calls[curr]
            print("{} calls {}!".format(name, calls[curr]))
            print()
            time.sleep(SLEEP_TIME)
        return calls

    def startHand(self, first, lastHand):
        currHand = Hand(first, lastHand, self.names, self.players, self.calls, 
            self.wins, self.power, self.cardRanker, self.shown, self.cardRange
        )
        currHand.playHand()
        self.hands.append(currHand)
        return currHand.getWinner()

    def getDiffs(self):
        return self.diffs
