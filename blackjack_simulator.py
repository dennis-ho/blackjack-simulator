#!/usr/bin/env python

import argparse
import csv
import logging
import math
import random

H = 'H'
S = 'S'
Dh = 'DH'
Ds = 'DS'
P = 'P'
Ph = 'PH'
Rh = 'RH'
Rs = 'RS'
Rp = 'RP'

split_strategy = [
    #2   3   4   5   6   7   8   9   10  A
    [Ph, Ph, P,  P,  P,  P,  H,  H,  H,  H],   # 2/2
    [Ph, Ph, P,  P,  P,  P,  H,  H,  H,  H],   # 3/3
    [H,  H,  H,  Ph, Ph, H,  H,  H,  H,  H],   # 4/4
    [Dh, Dh, Dh, Dh, Dh, Dh, Dh, Dh, H,  H],   # 5/5
    [Ph, P,  P,  P,  P,  H,  H,  H,  H,  H],   # 6/6
    [P,  P,  P,  P,  P,  P,  H,  H,  H,  H],   # 7/7
    [P,  P,  P,  P,  P,  P,  P,  P,  P,  Rp],  # 8/8
    [P,  P,  P,  P,  P,  S,  P,  P,  S,  S],   # 9/9
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],   # 10/10
    [P,  P,  P,  P,  P,  P,  P,  P,  P,  P],   # A/A
]

soft_strategy = [
    #2   3   4   5   6   7   8   9   10  A
    [H,  H,  H,  Dh, Dh, H,  H,  H,  H,  H],  # 13
    [H,  H,  H,  Dh, Dh, H,  H,  H,  H,  H],  # 14
    [H,  H,  Dh, Dh, Dh, H,  H,  H,  H,  H],  # 15
    [H,  H,  Dh, Dh, Dh, H,  H,  H,  H,  H],  # 16
    [H,  Dh, Dh, Dh, Dh, H,  H,  H,  H,  H],  # 17
    [Ds, Ds, Ds, Ds, Ds, S,  S,  H,  H,  H],  # 18
    [S,  S,  S,  S,  Ds, S,  S,  S,  S,  S],  # 19
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],  # 20
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],  # 21
]

hard_strategy = [
    #2   3   4   5   6   7   8   9   10  A
    [H,  H,  H,  H,  H,  H,  H,  H,  H,  H],   # 4
    [H,  H,  H,  H,  H,  H,  H,  H,  H,  H],   # 5
    [H,  H,  H,  H,  H,  H,  H,  H,  H,  H],   # 6
    [H,  H,  H,  H,  H,  H,  H,  H,  H,  H],   # 7
    [H,  H,  H,  H,  H,  H,  H,  H,  H,  H],   # 8
    [H,  Dh, Dh, Dh, Dh, H,  H,  H,  H,  H],   # 9
    [Dh, Dh, Dh, Dh, Dh, Dh, Dh, Dh, H,  H],   # 10
    [Dh, Dh, Dh, Dh, Dh, Dh, Dh, Dh, Dh, Dh],  # 11
    [H,  H,  S,  S,  S,  H,  H,  H,  H,  H],   # 12
    [S,  S,  S,  S,  S,  H,  H,  H,  H,  H],   # 13
    [S,  S,  S,  S,  S,  H,  H,  H,  H,  H],   # 14
    [S,  S,  S,  S,  S,  H,  H,  H,  Rh, Rh],  # 15
    [S,  S,  S,  S,  S,  H,  H,  Rh, Rh, Rh],  # 16
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  Rs],  # 17
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],   # 18
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],   # 19
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],   # 20
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],   # 21
]


def insurance_strategy_counting(table):
    return 'I' if table.true_count() >= 2.3 else 'N'


def insurance_strategy_never(table):
    return 'N'


def insurance_strategy_even_money(table):
    return 'I' if table.curr().is_blackjack() == 21 else 'N'


def basic_strategy(table, available_actions):
    if 'I' in available_actions:
        action = insurance_strategy_never(table)
    elif 'P' in available_actions:
        action = split_strategy[table.curr().cards[0] - 2][table.dealer_hand.cards[0] - 2]
    elif table.curr().is_soft():
        action = soft_strategy[table.curr().value() - 13][table.dealer_hand.cards[0] - 2]
    else:
        action = hard_strategy[table.curr().value() - 4][table.dealer_hand.cards[0] - 2]
    return action[0] if action[0] in available_actions else action[1]


def count_hi_lo(cards):
    count_val = sum([1 if card in [2, 3, 4, 5, 6] else -1 if card in [10, 11] else 0 for card in cards])
    return count_val


class Hand:
    def __init__(self):
        self.cards = []
        self.bet = 1
        self.actions = []
        self.insured = False
        self.surrendered = False
        self.from_split = False
        self.count_hist = []

    def value(self):
        hand_val = sum(self.cards)
        soft_aces = sum(1 for card in self.cards if card == 11)
        while hand_val > 21 and soft_aces > 0:
            hand_val -= 10
            soft_aces -= 1
        return hand_val

    def is_blackjack(self):
        return self.value() == 21 and len(self.cards) == 2 and self.from_split is False

    def is_soft(self):
        hand_val = sum(self.cards)
        soft_aces = sum(1 for card in self.cards if card == 11)
        while hand_val > 21 and soft_aces > 0:
            hand_val -= 10
            soft_aces -= 1
        return soft_aces > 0

    def __repr__(self):
        return str(self.cards)


class Table:
    def __init__(self):
        self.shoe = []
        self.shoe_id = -1
        self.dealer_hand = Hand()
        self.player_hand = [Hand()]
        self.curr_idx = 0
        self.cards_remaining = 0
        self.shuffle_pending = False

    def new_shoe(self, decks=8, penetration=6.5):
        self.shoe_id += 1
        self.shoe = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4 * decks
        random.shuffle(self.shoe)
        self.shoe.insert(int(math.floor(penetration * 52)), 0)  # 0 value card indicates cut card
        self.cards_remaining = len(self.shoe)
        self.shuffle_pending = False

    def initial_deal(self):
        self.dealer_hand = Hand()
        self.player_hand = [Hand()]
        self.curr_idx = 0
        self.cards_remaining = len(self.shoe)

        self.player_hand[0].count_hist.append((self.run_count(), self.true_count()))
        self.player_hand[0].cards.append(self.next_card())
        self.dealer_hand.cards.append(self.next_card())
        self.player_hand[0].cards.append(self.next_card())
        self.dealer_hand.cards.append(self.next_card())

    def next_card(self):
        card = self.shoe.pop(0)
        if card == 0:  # Cut card
            self.shuffle_pending = True
            card = self.shoe.pop(0)
        return card

    def curr(self):
        return self.player_hand[self.curr_idx]

    def total_bet(self):
        return sum([hand.bet for hand in self.player_hand])

    def num_actions_taken(self):
        return sum([len(hand.actions) for hand in self.player_hand])

    def available_actions(self):
        actions = []

        if self.curr_idx is None:  # All player hands finished
            return actions

        if self.dealer_hand.cards[0] == 11 and self.num_actions_taken() == 0:
            actions.append('I')
            actions.append('N')
            return actions

        if len(self.curr().actions) == 0:
            actions.append('D')  # Note: Double down on blackjack is not wise but surprisingly is technically allowed

        if len(self.curr().actions) == 0 and self.curr_idx == 0:  # Can not surrender after split
            actions.append('R')

        if len(self.player_hand) < 4 and len(self.curr().cards) == 2 and self.curr().cards[0] == self.curr().cards[1]:
            if self.curr().cards[0] != 11 or len(self.player_hand) == 1:  # Assumes re-splitting Aces is not allowed
                actions.append('P')

        if self.curr().value() <= 21:  # Note: You can still hit on 21 if you really want to
            actions.append('H')
            actions.append('S')

        return actions

    def do_action(self, action):
        self.curr().actions.append(action)
        self.curr().count_hist.append((self.run_count(), self.true_count()))

        if action == 'I':
            self.curr().insured = True
        if self.dealer_hand.is_blackjack():
            self.curr_idx = None
            return

        if action == 'D':
            self.curr().bet *= 2
        if action == 'H' or action == 'D':
            self.curr().cards.append(self.next_card())
        if action == 'P':
            new_hand = Hand()
            new_hand.from_split = True
            new_hand.cards.append(self.curr().cards.pop())
            self.player_hand.append(new_hand)
        if action == 'R':
            self.curr().surrendered = True
            self.curr().bet /= 2
        if action == 'S' or action == 'D' or action == 'R' or self.curr().value() > 21 or action is None:
            if self.curr_idx == len(self.player_hand) - 1:
                self.curr_idx = None
                self.finish_dealer_hand()
            else:
                self.curr_idx += 1
                self.curr().cards.append(self.next_card())

    def finish_dealer_hand(self):
        while self.dealer_hand.value() < 17 or self.dealer_hand.value() == 17 and self.dealer_hand.is_soft():
            self.dealer_hand.cards.append(self.next_card())

    def results(self):
        result_val = {
            'shoe_id': self.shoe_id,
            'cards_remaining': self.cards_remaining,  # Value at the START of the round before dealing cards
            'dealer_up': self.dealer_hand.cards[0],
            'initial_hand':
                self.player_hand[0].cards[:2] if len(self.player_hand) == 1 else [self.player_hand[0].cards[0]] * 2,
            'dealer_final': self.dealer_hand,
            'dealer_final_value': 'BJ' if self.dealer_hand.is_blackjack() else self.dealer_hand.value(),
            'player_final': self.player_hand,
            'player_final_value': ['BJ' if hand.is_blackjack() else hand.value() for hand in self.player_hand],
            'actions_taken': [hand.actions for hand in self.player_hand],
            'run_count': self.player_hand[0].count_hist[0][0],  # Value at the START of the round before dealing cards
            'true_count': self.player_hand[0].count_hist[0][1],  # Value at the START of the round before dealing cards
            'win': 0,
        }

        if self.player_hand[0].insured:
            insurance_cost = self.player_hand[0].bet * 0.5
            result_val['win'] -= insurance_cost  # Charge insurance

        if self.dealer_hand.is_blackjack():
            if self.player_hand[0].insured:
                result_val['win'] += insurance_cost * 3  # Insurance pays 2:1 plus return original charge
            if not self.player_hand[0].is_blackjack():
                result_val['win'] -= self.player_hand[0].bet
            return result_val

        for hand in self.player_hand:
            if hand.value() > 21:
                result_val['win'] -= hand.bet
            elif hand.is_blackjack():
                result_val['win'] += 1.5 * hand.bet
            elif hand.surrendered:
                result_val['win'] -= hand.bet
            elif hand.value() > self.dealer_hand.value():
                result_val['win'] += hand.bet
            elif hand.value() < self.dealer_hand.value():
                result_val['win'] -= hand.bet
            else:
                result_val['win'] += 0
        return result_val

    def run_count(self):
        return -count_hi_lo(self.shoe)

    def true_count(self):
        decks_remaining = len(self.shoe) / 52
        return math.trunc(self.run_count() / decks_remaining)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_path', help='Path to save CSV results', default='blackjack_simulator.csv')
    parser.add_argument('--log_path', help='Path to log file', default='blackjack_simulator.log')
    parser.add_argument('--log_level', help='Level of messages to write to log file', default='info')
    parser.add_argument('--hands', help='Number of hands to play', default=100)
    parser.add_argument('--decks', help='Number of decks to use in a shoe', default=8)
    parser.add_argument('--pen', help='Deck penetration (number of decks played before shuffling)', default=6.5)

    args = parser.parse_args()

    log_levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
    }
    log_level = log_levels[args.log_level.lower()]
    logging.basicConfig(filename=args.log_path, format='%(levelname)s:%(message)s', level=log_level, filemode='w')
    logging.info('Program arguments %s', args)

    csv_columns = [
        'shoe_id',
        'cards_remaining',
        'dealer_up',
        'initial_hand',
        'dealer_final',
        'dealer_final_value',
        'player_final',
        'player_final_value',
        'actions_taken',
        'run_count',
        'true_count',
        'win',
    ]
    with open(args.output_path, 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        csv_writer.writeheader()

    results_log = []
    table = Table()

    while len(results_log) < args.hands:
        table.new_shoe(args.decks, args.pen)

        while not table.shuffle_pending:
            table.initial_deal()
            while table.curr_idx is not None:
                logging.debug('dealer: %s', table.dealer_hand)
                logging.debug('player: %s', table.player_hand)

                logging.debug('current player hand index: %s', table.curr_idx)

                actions = table.available_actions()
                logging.debug('available actions: %s', actions)

                action = basic_strategy(table, actions) if len(actions) > 0 else None
                logging.debug('action taken: %s', action)
                table.do_action(action)

            logging.debug('dealer final: %s', table.dealer_hand)
            logging.debug('player final: %s', table.player_hand)

            logging.info('results: %s', table.results())
            results_log.append(table.results())

            with open(args.output_path, 'a') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                csv_writer.writerow(table.results())

            logging.debug('hands played: %s', len(results_log))

            logging.debug('-------------------------------')

            if len(results_log) >= args.hands:
                return


if __name__ == '__main__':
    main()
