'''
File for Softmax player class.
'''

from players.player import Player

'''
Class for logistic regression-based player.
Modelling approach for making calls:
	Making calls is treated as a multi-class classification problem (0, ..., n the number of cards)
	Different model for each round size (except 1-card round uses expected util)
	Treat features as continuous variables (all integral, but clearly ordered)
	Correct label is given at the end of the round as number of hands actually won
	Features used for making calls:
		Sum of calls made so far
		Number of players who've made calls
		Number of remaining players
		Number of remaining cards between each card in hand
			i.e. for an n-card hand, n + 1 buckets to place remaining cards
Modelling approach for playing cards:
	Also treated as a multi-class classification problem (top, second, third... etc ranked cards)
	Different model for each hand size (i.e. cards remaining to be played)
	Features still continuous (all integral)
	Uses a one vs rest regression model
	Classification is wrong if the player wins the hand and ultimately goes over, or vice versa
	Features used for playing cards:
		Number of remaining cards between each card in hand
		Number of remaining players
		Sum of calls made by remaining players
		Number of cancellation possibilities for top card
	 	Immediate rank of each card if chosen
'''
class Logistic(Player):
	pass