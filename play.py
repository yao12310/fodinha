'''
Core file for launching game of Fodinha.
'''

'''
To-Do List

Implementations:

TODO: General game logic
	>> Done
TODO: Manual player
	>> Done
TODO: Sort hands as players play cards
TODO: Logic for 1-card hand size rounds
	>> Done
TODO: Don't prompt for card index when only one card left
	>> Done
TODO: Logic for stopping Easy AI from making illegal calls
	>> Done
TODO: Logic for Easy AI on one-card hands
	>> Done
TODO: Medium AI, various upgrades on Easy:
	Adjust thresholds for calls based on the calls so far
	Non-random selection of cards during hands
	Find a way around assuming uniformity (perhaps Hard AI)
	Detect cancellations (especially on one-card hands)

Refactoring:

TODO: Util method for power card choice, requiring a specific kind of input (i.e. only y / n)
	>> Done
TODO: Decide whether to use dictionaries keyed on name in Game or just numerical indices
    >> Decided on numerical indices, only named____ variables use name keys
TODO: Break Game class into Game, Round, and Hand classes
    >> Done
TODO: Have the power card be represented by an int, not the string rank
	>> Done
TODO: Divide player class into abstract class and manual player class
	>> Done
TODO: Pass in illegal call information from round instead of computing in Player
	>> Done
TODO: History class instead of each object housing separate info, pass reference around
TODO: Move different player types into individual files
	>> Done
TODO: Move utils and game play classes into separate directories
	>> Done

Bug Fixes:

TODO: Fix dealer update logic, perhaps by not modifying names / players and using elim
	>> Done
TODO: Edge case handling for simultaneous loss (negative lives)
	>> Done
TODO: Edge case handling for when the entire hand cancels
TODO: Fix winner not going first in the next hand
	>> Done
TODO: Suits shouldn't matter when ranking in AI (except power) -- use cardRanker but preserve O(n)

Misc:

TODO: Doc strings for Player classes
	>> Done
TODO: Show "Cancelled" instead of "None"
TODO: Print dictionaries more cleanly instead of on one line (also, order entries by play)
TODO: Plural vs singular when updating life counts
TODO: README with rules and project overview
	>> Done
TODO: Exception for non-implemented player classes
'''

from logic.game import Game
import sys

cardRange = int(sys.argv[1])
numLives = int(sys.argv[2])
powerTries = int(sys.argv[3])
names = sys.argv[4:]

game = Game(names, cardRange, numLives, powerTries)
game.playGame()