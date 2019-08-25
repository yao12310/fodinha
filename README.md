# Fodinha (Oh Hell) Overview

Fodinha, known in English as "Oh Hell", is a multi-player card game. In the rules variation playable in this project, each player starts the game with the same number of lives, and rounds are played until there is only one player remaining. Each round is comprised of some number of hands, in each of which the players all play one card: the player who plays the highest card is designated as the winner of that hand. At the beginning of each round, players receive their cards and predict the number of hands they will win. At the end of a round, each player loses lives according to the absolute difference of their original prediction and the actual number of wins.

In this project, logic for playing the game was implemented in Python. Currently, the game is playable via command line: a UI for gameplay will be implemented, but the current focus is on building agents for automated gameplay.

For more information about the game, see https://en.wikipedia.org/wiki/Oh_Hell.

## How to Play

### Formal Rules

 * Each player starts with the same number of lives.
 * In each round, a player is designated as the dealer, which rotates round to round.
 * The ranking of cards changes slightly each round:
   * Ace is always the lowest.
   * The max card rank is selected at the beginning of the game.
   * Then, the default ranking is just A to the highest rank.
   * In each round, a power card is selected by the dealer, who draws from the remaining deck.
     * The card rank immediately above the drawn card is a candidate (i.e. if 9 is drawn, 10 is a candidate).
     * The dealer can either reject or approve the candidate, following a rejection, another candidate is chosen.
     * At the beginning of the game, the max number of candidates that are allowed is selected.
     * Once this max number has been reached, the power card is forced.
     * Note that the dealer can't see their cards before selecting the power card.
   * Then, this power card becomes the highest card for that round.
   * In general, suits don't matter for card rankings
     * Cards of the same rank "cancel" when played.
     * Power cards are ranked by suit: Spades > Hearts > Clubs > Diamonds.
 * Rounds are played, starting with a one-card round and incrementing by 1 in each round.
   * If the incremented number of cards in a round would exceed the total deck size minus the maximum number of power candidates, then the round size decrements until it reaches 1 again.
   * Once cards have been dealt, players take turns calling the number of hands they expect to win.
     * The player immediately after the dealer calls first.
     * This progresses until reaching back to the dealer, who always calls last.
     * The dealer cannot make a call if that call would make the sum of all calls equal the size of the round.
     * For example, if the initial calls are 1, 0, and 2 for a 4 card hand, the dealer cannot call 1.
 * After calls are made, a series of hands are played
   * Each hand requires that each player play one card.
   * Cards are ranked according to the ranking described above, and a winner is selected.
   * With the exception of power cards, cards of the same rank "cancel".
     * They are removed from play, so the corresponding players can't win the round.
     * If every card is cancelled, then the next hand counts for an extra win.
     * If every card is cancelled in every hand in a round, then no wins are given for the entire round.
 * Once all hands have been played, the number of wins for each player is counted.
   * Each player loses lives according to how much their call was off from their actual number of wins (absolute difference).
   * Players are eliminated at this phase if their remaining life count is non-positive.
 * The game is won once only one player with lives remains.
   * If all players would be eliminated, the player with the least negative lives still wins.
   * If all players would be eliminated with the same number of lives, then another round is played.

### Python Script

Playing the game can be done by running the Python script ```play.py```, with arguments ```range, lives, tries, names```:

 * ```range```: positive integer (at most 13) representing the number of card ranks used.
 * ```lives```: positive integer representing the number of lives each player begins the game with.
 * ```tries```: positive integer representing the number of tries a player has to select a power card.
 * ```names```: list of strings representing the names of the players in the game.

## Project Technical Overview

### Game Logic

Logic for the game follows an object-oriented paradigm, with classes representing the overall ```Game``` and individually played ```Rounds``` and ```Hand``` instances. More documentation can be found in the respective files reflecting the design of these objects.

### Automated Play

Similarly, players of the game are also represented as objects, with several variations. To include one of these agents in a game, use a name that contains the appropriate string (i.e. for an Easy agent, include a player named ```EASY_1```).

**Completed Implementations:**

*Game data given below come from trials of 10,000 4 player games with standard settings of 5 lives, card range 10, and 3 power tries.*

*Technical details for the latter two agent types can be found in documentation in their implementation files: ```prob.py``` and ```reinforcement.py```.*

 * Manual (default), which represents live human players.
 * Random agents (```RANDOM```), which play the game completely randomly (used as a benchmark)
 * Expected utility-based agents, with several variations of difficulty:
   * Easy (```EASY```): Which compute expected values of and play cards randomly.
     * Models card play as hypergeometric distribution to compute expected number of wins
     * Despite still largely random play, performs quite well: wins over 91% of games versus Random agents
   * Hard (```HARD```): Similar to Easy, but do not play cards randomly.
     * Computes probability of victory for current hand and future hands for all cards in hand
     * Chooses card play that minimizes difference between future expected wins and remaining calls
     * Plays nearly optimally given the assumption of random play: wins 97% of games versus Random agents
     * Despite identical strategy for making calls, improvement in card play gives agent average place of 1.6 versus Easy agents (average 2.6 place).
 * Reinforcement learning-based agents, which apply reinforcement learning.
   * QLearning (```Q_LEARN```): Learn Q-values through experience (epsilon greedy)
     * Models state using total number of players, calls / plays so far, cards in hand, players calling / playing after agent
     * Performs Bellman updates and caches values of (state, action) pairings
     * Takes random actions to further exploration of state space
     * Poor performance possibly due to size of state space, wins <10% of games against Easy agents.
   * QApproximate (```Q_APPROXIMATE```): Learn weights for approximating Q-values linearly
     * Resolves state space size issue by learning weights for linear approximation of Q-values
     * See code documentation for specific features designed for use in making calls and playing cards.

**Future Implementations:**
 * Search-based agents (```SEARCH```), which play the game using search algorithms.
 * Classification-based agents, which use learning to solve decisions in the game as classification problems:
   * Softmax (```LOGISTIC```): Simple multinomial logistic regression model.
   * Neural Network (```NEURAL_NET```): Neural Network-based play.

