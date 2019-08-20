'''
File for Hand class.
'''

'''
Hand stores hand-level information:
    Game and round info and meta hand settings passed down from Round:
        Game: List of names and Player objects
        Round: Original calls, current wins, power card, comparison fn
        Meta: First player in the hand, whether it is the last hand of the round
Funcitonalities:
    Calls on Player instances to select cards
    Tracks winner (passes back up to Round)
'''
class Hand:

    def __init__(self, first, lastHand, names, players, calls, wins, power, cardRanker):
        self.first = first
        self.lastHand = lastHand
        self.names = names
        self.players = players
        self.calls = calls
        self.wins = wins
        self.power = power
        self.cardRanker = cardRanker
        self.numPlayers = len(names)

    def playHand(self):
        self.plays = [None] * self.numPlayers
        namedCalls = {self.names[i]: self.calls[i] for i in range(self.numPlayers)}
        namedWins = {self.names[i]: self.wins[i] for i in range(self.numPlayers)}

        for i in range(self.numPlayers):
            curr = (self.first + i) % self.numPlayers
            name = self.names[curr]
            choice = self.players[curr].chooseCard(
                namedCalls, namedWins, self.lastHand, self.power,
                {self.names[j]: str(self.plays[j]) for j in range(self.numPlayers)}
            )

            if choice.num != self.power:
                cancelled = self.checkCancel(name, choice)
                if not cancelled:
                    self.plays[curr] = choice
            else:
                self.plays[curr] = choice

        if not any(self.plays):
            print("All hands cancelled this round!")
            print("Win will carry over to the next round.")
            self.winner = None
        else:
            self.winner = self.plays.index(max(self.plays, key = self.cardRanker))
            print("Final plays were: {}"
                .format({self.names[i]: str(self.plays[i]) for i in range(self.numPlayers)})
            )
            print("The winner of the hand, playing a {}, is {}!".format(self.plays[self.winner], self.names[self.winner]))

    def checkCancel(self, name, choice):
        for i in range(self.numPlayers):
            if not self.plays[i]:
                continue
            if self.plays[i].rank == choice.rank:
                print("{}'s {} cancelled with {}'s {}!"
                    .format(name, str(choice), self.names[i], str(self.plays[i]))
                )
                print()
                self.plays[i] = None
                return True
        return False

    def getWinner(self):
        return self.winner
