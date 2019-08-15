'''
File for Game class.
'''

import time
from logic.round import Round
from players.choose import chooseStrategy
from utils.card import CardCollection
from utils.constants import SLEEP_TIME

'''
Top level object, stores highest level information:
    Meta game settings passed down from play.py:
        Names (creates list of player objects), card range, number of lives, tries for power card
    Game state:
        Current round, current dealer, winner of game, eliminated players
    Game history: Rounds played
Functionalities:
    Initializes player and deck objects
    Houses logic for game ending and round progression (updates lives and dealer)
    Launches Round instances (passes down names, players, deck, range of cards)
'''
class Game:

    def __init__(self, names, cardRange, numLives, powerTries):
        self.rounds = []
        self.names = names
        self.players = [chooseStrategy(name, numLives, self.rounds) for name in names]
        self.cardRange = cardRange
        self.deck = CardCollection(cardRange = cardRange)
        self.numPlayers = len(names)
        self.powerTries = powerTries

    def playGame(self):
        self.round = 1
        self.winner = None
        self.dealer = 0
        self.elim = []

        print("Initiating game!")

        while not self.winner:
            # Play the current round, get results
            diffs = self.startRound()

            # Use results to update lives, check for eliminations
            elims = self.updateLives(diffs)

            # If eliminations, update roster
            if elims:
                self.updateRoster(elims)

            # Check for winner
            self.winner = self.checkWinner()

            # Update game progress
            self.updateRound()

        print("Game over! The winner is {}.".format(self.winner))
        standString = "Final Standings:"
        standings = [self.winner] + self.elim[::-1]
        rank = 1
        for name in standings:
            standString += "\n\t{}) {}".format(rank, name)
            rank += 1
        print(standString)

    def startRound(self):
        print("Beginning round with {} cards. Dealer is {}.".format(self.round, self.names[self.dealer]))
        currRound = Round(self.round, self.dealer, self.names, self.players, self.deck, self.cardRange, self.powerTries)
        currRound.playRound()
        self.rounds.append(currRound)
        print()
        time.sleep(SLEEP_TIME)
        return currRound.getDiffs()

    def updateLives(self, diffs):
        print("Updating life counts...")
        newElims = []
        for i in range(self.numPlayers):
            lives = self.players[i].loseLives(diffs[i])
            if lives <= 0:
                newElims.append(i)
        print()
        time.sleep(SLEEP_TIME)
        return newElims[::-1]

    def updateRoster(self, elims):
        print("Eliminating players...")
        for nameIndex in elims:
            name = self.names.pop(nameIndex)
            self.players.pop(nameIndex)
            self.elim.append(name)
            self.numPlayers -= 1
            print("{} has been eliminated! {} players remain.".format(name, self.numPlayers))
        print()
        time.sleep(SLEEP_TIME)

    def checkWinner(self):
        if self.numPlayers == 1:
            return self.names[0]

    def updateRound(self):
        self.dealer = (self.dealer + 1) % self.numPlayers
        if (self.round + 1) * self.numPlayers > (self.cardRange * 4 - self.powerTries):
            self.round -= 1
        else:
            self.round += 1
