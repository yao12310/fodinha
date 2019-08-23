'''
File for abstract Player class.
'''

'''
Abstract class for players.
Player stores player-level information:
    Player game status passed down from game.py:
        Name of player, number of lives remaining, and access to rounds history
    Player game history:
        Hands had, calls made, lives lost
    Player round information:
        Current hand (passed down from round.py), current call
        Card ranker for the current round is also passed down, used by computer players
Functionalities:
    Game-level updates:
        Setting hand and losing lives (info passed down from game.py)
    Round-level decisions (abstract methods):
        Choosing power card: given a card num from round.py, return yes / no decision
        Making call: given current round info, return int for round call
        Choosing card: given current hand info, return choice of Card
'''
class Player:

    # Implemented methods for game-level updates and information passing

    def __init__(self, name, numLives, history):
        self.name = name
        self.lives = numLives
        self.history = history
        self.hands = []
        self.calls = []
        self.lost = []
        self.currHand = []
        self.currCall = None

    def setHand(self, hand):
        self.currHand = hand
        self.hands.append(hand.copy())

    def loseLives(self, lost):
        self.lost.append(lost)
        self.lives -= lost
        print("{} has lost {} lives! {} lives remaining.".format(self.name, lost, self.lives))
        return self.lives

    def setLives(self, lives):
        self.lives = lives

    # Abstract methods for round-level updates
    def choosePower(self, cand, shown):
        pass

    def makeCall(self, currCalls, numPlayers, roundNum, power, shown, illegal, cardRange, cardRanker, namedDeals = {}):
        pass

    def chooseCard(self, calls, wins, lastHand, power, plays, namedPlays, shown, cardRange):
        pass
