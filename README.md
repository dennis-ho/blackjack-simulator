# blackjack-simulator

This script was created to produce a dataset of simulated Blackjack hands found here:

https://www.kaggle.com/dennisho/100-million-blackjack-hands

## Description

#### This script simulates blackjack hands according to the most common set of rules in Las Vegas casinos:
* 8 deck shoe (6.5 deck penetration) (Configureable)
* 1st card of shoe is burned
* Blackjack pays 3:2
* Double down allowed on any first 2 cards
* Double down after split allowed
* Split any same first 2 cards up to 4 hands
* Re-splitting Aces is not allowed
* Splitting Aces receives 1 extra card only, no Blackjack
* Late surrender allowed
* No surrender after split
* Dealer hits soft 17

#### Things to note:
* All hands are played "heads up" (single player vs the dealer)
* The player will always play according to correct Basic Strategy
* Starting bet for each hand is always 1
* 10's, J's, Q's, K's are all considered the same in Blackjack and are all represented as 10's
* A's are all represented as 11's
* Suits are irrelevant and not considered
* Run count and True count values (truncated to Integer precision) are recorded according to the Hi-Lo system at the start of each round before any cards are dealt
* The number of cards remaining in the shoe is recorded at the start of each round before any cards are dealt. This number includes cards which will not be played due to less than 100% deck penetration


#### The actions taken by the player are represented as follows:
| Action | Description |
| --- | --- |
| H | Hit |
| S	| Stand |
| D	| Double Down |
| P	| Split |
| R	| Surrender |
| I	| Buy Insurance (Never used since player is following Basic Strategy) |
| N	| No Insurance |

## Getting Started

### Dependencies

Python 3

### Executing program

```
python3 blackjack-simulator.py
```

#### Parameters
| Parameter | Description | Default |
| --- | --- | --- |
| --output_path | Path to save CSV results | blackjack_simulator.csv |
| --log_path | Path to log file | blackjack_simulator.log |
| --log_level | Level of messages to write to log file | info |
| --hands | Number of hands to play | 100 |
| --decks | Number of decks to use in a shoe | 8 |
| --pen | Deck penetration (number of decks played before shuffling) | 6.5 |


## Authors

Dennis Ho

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

Basic Strategy Chart: [Wizard of Odds](https://wizardofodds.com/games/blackjack/strategy/4-decks/)
