'''
Util file for Card-related classes.
'''

import itertools
import random

'''
Class for data structure representing collection of cards, used for decks, player hands, and lists of shown cards
CardCollection houses a list of Card objects, and provides methods for shuffling and dealing cards
'''
class CardCollection:

    def __init__(self, cardRange = None, cards = []):
        if cards:
            self.cards = cards
        elif cardRange:
            self.cards = [
                Card(num, suit) for (num, suit) in 
                list(itertools.product(range(cardRange), CardInfo.SUITS))
            ]
        elif not cardRange and not cards:
            self.cards = []

    def deal(self, numCards, numHands):
        return [
            CardCollection(cards = self.cards[(i * numCards):((i + 1) * numCards)]) for i in range(numHands)
        ]

    def shuffle(self):
        random.shuffle(self.cards)

    def slice(self, start, end):
        return CardCollection(cards = self.cards[start:end])

    def get(self, index):
        return self.cards[index]

    def append(self, card):
        self.cards.append(card)

    def pop(self, index = -1):
        return self.cards.pop(index)

    def copy(self):
        return CardCollection(cards = list(self.cards))

    def __str__(self):
        return str([str(card) for card in self.cards])

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        yield from self.cards

'''
Class for representing cards
Each card stores a number and a suit, as well as a string-translated rank
'''
class Card:

    def __init__(self, num, suit):
        self.num = num
        self.suit = suit
        self.rank = CardInfo.RANKS[num]

    def __str__(self):
        return self.rank + " of " + self.suit

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return (self.num == other.num) and (self.suit == other.suit)

    def __hash__(self):
        return hash((self.num, self.suit))

    def __contains__(self, item):
        return any([item == card for card in self.cards])

'''
Static class for card information
Stores information on suits, ranks, and comparison
'''
class CardInfo:

    SPADES = "Spades"
    HEARTS = "Hearts"
    CLUBS = "Clubs"
    DIAMONDS = "Diamonds"

    SUITS = [DIAMONDS, CLUBS, HEARTS, SPADES]
    SUIT_RANKS = {SPADES: 3, HEARTS: 2, CLUBS: 1, DIAMONDS: 0}

    RANKS = [
        "A", "2", "3", "4", "5", "6", 
        "7", "8", "9", "10", "J", "Q", "K"
    ]

'''
Static class for card utils
Stores methods for ranking cards and joining collections
'''
class CardUtils:
    def cardRankerGen(power, cardRange):
        def cardRanker(card):
            if not card:
                return -1
            if card.num != power:
                return card.num
            return cardRange + CardInfo.SUIT_RANKS[card.suit]
        return cardRanker

    def joinCollections(collect1, collect2):
        return CardCollection(collect1.cards + collect2.cards)