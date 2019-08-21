'''
File for Manual player class.
'''

import time

from players.player import Player
from utils.card import CardInfo
from utils.constants import SLEEP_TIME
from utils.constants import POWER_YES
from utils.constants import POWER_NO

'''
Class for human player.
Implements round-level decisions via user input in terminal.
'''
class Manual(Player):

    def choosePower(self, cand, shown):
        decision = input("{}, would you like for {} to be the power card? [{}/{}]: ".format(self.name, CardInfo.RANKS[cand], POWER_YES, POWER_NO))
        if decision == POWER_YES or decision == POWER_NO:
            return decision
        else:
            print("You must enter either {} or {} for your decision!".format(POWER_YES, POWER_NO))
            return self.choosePrompt(cand)

    def makeCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals = {}):
        if namedDeals:
            print("Current Information \nCurrent Calls: {} \nNumber of Players: {} \nRound: {} \nPower: {} \nShown: {} \nHands: {}"
                    .format(currCalls, numPlayers, roundNum, CardInfo.RANKS[power], shown, 
                        {name: str(card) for (name, card) in namedDeals.items() if name != self.name}))
        else:
            print("Current Information \nCurrent Calls: {} \nNumber of Players: {} \nRound: {} \nPower: {} \nShown: {} \nHand: {}"
                    .format(currCalls, numPlayers, roundNum, CardInfo.RANKS[power], shown, self.currHand))

        if illegal >= 0:
            print("You are the last player to make a call this round! You cannot call {}.".format(illegal))

        try:
            call = int(input("{}, submit your call for this round: ".format(self.name)))
        except ValueError as e:
            print("You have entered a non-numerical value! You must re-choose.")
            return self.makeCall(currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, namedDeals)

        if call < 0:
            print("Calls must be non-negative! You must re-call.")
            return self.makeCall(currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, namedDeals)
        if call == illegal:
            print("You have made an illegal call! You must re-call.")
            return self.makeCall(currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, namedDeals)

        self.currCall = call
        self.calls.append(call)
        return call

    def chooseCard(self, calls, wins, lastHand, power, plays, namedPlays, shown, cardRange):
        if lastHand:
            choice = self.currHand.pop()
            print("{} played the {}.".format(self.name, str(choice)))
            time.sleep(SLEEP_TIME)
            return choice
        print("It is currently {}'s turn to choose a card.".format(self.name))
        print("Current Information \nCalls: {} \nWins: {} \nPlays: {} \nPower: {} \nShown Cards: {}"
                .format(calls, wins, namedPlays, CardInfo.RANKS[power], shown))
        print("Your Hand: {}".format(self.currHand))
        try:
            index = int(input("{}, submit the index of your choice of card (0-indexed): ".format(self.name)))
        except ValueError as e:
            print("You have entered a non-numerical value! You must re-choose.")
            return self.chooseCard(calls, wins, plays, namedPlays, power, plays)

        if index < 0 or index >= len(self.currHand):
            print("You have made an illegal selection! You must re-choose.")
            return self.chooseCard(calls, wins, plays, namedPlays, power, plays)

        choice = self.currHand.pop(index)
        print("{} played the {}.".format(self.name, str(choice)))
        print()
        return choice