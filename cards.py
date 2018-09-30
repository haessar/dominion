from termcolor import colored
import numpy as np


VICTORY_COUNT = 8
ACTION_COUNT = 10


class FailedAction(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class Card:
    color = 'white'

    def __init__(self, name, cost, initial):
        self.name = name
        self.cost = cost
        self.initial = initial
        self.fields = {'name': name, 'cost': cost, 'initial': initial}

    def __repr__(self):
        repr_fmt = ', '.join('{}={}'.format(k, v) for k, v in self.fields.items())
        return colored(self.__class__.__name__ + '({})'.format(repr_fmt), self.color)


class Action(Card):
    hand = None
    color = 'red'

    def __init__(self, *args, actions):
        super().__init__(*args)
        self.actions = actions
        self.fields['actions'] = actions

    def play(self, hand):
        self.hand = hand
        self.hand.actions -= 1

    def plus_cards(self, count):
        self.hand.cards.extend(self.hand.deck.draw(count))

    def plus_actions(self, count):
        self.hand.actions += count

    def plus_buys(self, count):
        self.hand.buys += count

    def plus_money(self, count):
        self.hand.money += count

    def gain(self, _max, pool=False):
        try:
            print(self.hand.table)
            while True:
                resp = input('Gain a card costing up to {}'.format(_max))
                if resp not in self.hand.table:
                    print('{} not a valid choice.'.format(resp))
                else:
                    if get(resp).cost <= _max:
                        break
            # Choose to gain onto discard or deck
            deck = self.hand.deck.discard if not pool else self.hand.deck.pool
            deck.extend(self.hand.table.draw(resp, 1))
        except Exception:
            raise FailedAction

    def trash(self, opt):
        try:
            while True:
                if isinstance(opt, int):
                    print(self.hand)
                    resp = input('Trash up to {} cards from your hand (comma separated):'.format(opt))
                    resp = [r.strip() for r in resp.split(',')]
                    if len(resp) <= opt:
                        break
                    else:
                        print('Please choose a maximum of {} cards to trash.'.format(opt))
                elif isinstance(opt, str):
                    break
            self.hand.trash(opt)
        except Exception:
            raise FailedAction

    def discard(self):
        pass

    def draw(self):
        pass


class Attack(Action):
    pass


class Reaction(Action):
    color = 'blue'


class Treasure(Card):
    color = 'yellow'

    def __init__(self, *args, value):
        super().__init__(*args)
        self.value = value
        self.fields['value'] = value


class Victory(Card):
    color = 'green'

    def __init__(self, *args, points):
        super().__init__(*args)
        self.points = points
        self.fields['points'] = points


class Set(dict):
    def draw(self, name, count):
        avail = self.get(name, 0)
        if count <= avail:
            self[name] -= count
            return [card for card in all_cards if card.name == name] * count

    def non_empty_piles(self):
        return [k for k, v in self.items() if v > 0]

    def empty_piles(self):
        return [k for k, v in self.items() if v == 0]


treasure_set = {
    Treasure('copper', 0, 50, value=1),
    Treasure('silver', 3, 40, value=2),
    Treasure('gold', 6, 30, value=3),
}

victory_set = {
    Victory('estate', 2, VICTORY_COUNT + 6, points=1),
    Victory('duchy', 5, VICTORY_COUNT, points=3),
    Victory('province', 8, VICTORY_COUNT, points=6),
}

base_set = {
    Action('cellar', 2, ACTION_COUNT, actions=[]),
    Action('chapel', 2, ACTION_COUNT, actions=[('trash', 4)]),
    Reaction('moat', 2, ACTION_COUNT, actions=[]),
    Action('harbinger', 3, ACTION_COUNT, actions=[]),
    Action('merchant', 3, ACTION_COUNT, actions=[]),
    Action('vassal', 3, ACTION_COUNT, actions=[]),
    Action('village', 3, ACTION_COUNT, actions=[('plus_actions', 2), ('plus_cards', 1)]),
    Action('workshop', 3, ACTION_COUNT, actions=[('gain', 4)]),
    Attack('bureaucrat', 4, ACTION_COUNT, actions=[]),
    Victory('gardens', 4, VICTORY_COUNT, points=lambda x: np.floor(len(x)/10)),
    Attack('militia', 4, ACTION_COUNT, actions=[]),
    Action('moneylender', 4, ACTION_COUNT, actions=[]),
    Action('poacher', 4, ACTION_COUNT, actions=[]),
    Action('remodel', 4, ACTION_COUNT, actions=[]),
    Action('smithy', 4, ACTION_COUNT, actions=[('plus_cards', 3)]),
    Action('throne_room', 4, ACTION_COUNT, actions=[]),
    Attack('bandit', 5, ACTION_COUNT, actions=[]),
    Action('council_room', 5, ACTION_COUNT, actions=[]),
    Action('festival', 5, ACTION_COUNT, actions=[('plus_actions', 2), ('plus_buys', 1), ('plus_money', 2)]),
    Action('laboratory', 5, ACTION_COUNT, actions=[('plus_actions', 1), ('plus_cards', 2)]),
    Action('library', 5, ACTION_COUNT, actions=[]),
    Action('market', 5, ACTION_COUNT, actions=[('plus_cards', 1), ('plus_actions', 1), ('plus_buys', 1), ('plus_money', 1)]),
    Action('mine', 5, ACTION_COUNT, actions=[]),
    Action('sentry', 5, ACTION_COUNT, actions=[]),
    Attack('witch', 5, ACTION_COUNT, actions=[]),
    Action('artisan', 6, ACTION_COUNT, actions=[]),
}

all_cards = base_set.union(treasure_set, victory_set)


def get(name):
    for c in all_cards:
        if c.name == name:
            return c
