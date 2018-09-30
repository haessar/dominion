import random

import numpy as np

import cards

identifiers = cards.base_set.copy()


def pref_default(avail):
    return random.sample(avail, 1)[0]


def pref_highest_cost(avail):
    choice = sorted(avail, key=lambda x: x.cost, reverse=True)
    choice = [c for c in choice if c.cost == choice[0].cost]
    return random.sample(choice, 1)[0]

def pref_big_money(avail):
    choice = [c for c in avail if c.name == 'province']
    if choice:
        return choice[0]
    else:
        choice = [c for c in avail if isinstance(c, cards.Treasure)]
        choice = sorted(choice, key=lambda x: x.cost, reverse=True)
        return choice[0]


# buy_pref = pref_highest_cost


class Table:
    turn = 0

    def __init__(self):
        self.supply = random.sample(identifiers, 10)
        self.supply = self.build_set(self.supply)
        self.treasures = self.build_set(cards.treasure_set)
        self.victories = self.build_set(cards.victory_set)

    def __repr__(self):
        all = self.all()
        avail = []
        for c in cards.all_cards:
            if c.name in all.non_empty_piles():
                avail.append((c.name, c.cost, all.get(c.name)))
        avail = sorted(avail, key=lambda x: [x[1], x[0]])
        return '{:>14} {:>14} {:>14}\n'.format('CARD', 'COST', 'NUM') + '\n'.join('{:>14} {:>14} {:>14}'.format(*c) for c in avail)

    def __iter__(self):
        for c in self.all().non_empty_piles():
            yield c

    @staticmethod
    def build_set(_set):
        return cards.Set({card.name: card.initial for card in _set})

    def all(self):
        pile = cards.Set()
        pile.update(self.victories)
        pile.update(self.treasures)
        pile.update(self.supply)
        return pile

    def get_set(self, item):
        for pile in [self.supply, self.treasures, self.victories]:
            if item in pile:
                return pile

    def draw(self, choice, count):
        return self.get_set(choice).draw(choice, count)


class Deck:
    def __init__(self, table, buy_pref=pref_big_money):
        self.pool = table.treasures.draw('copper', 7) + table.victories.draw('estate', 3)
        random.shuffle(self.pool)
        self.discard = []
        self.trash = []
        self.played = []
        self.buy_pref = buy_pref

    def draw(self, count):
        _cards = []
        avail = len(self.pool)
        if avail >= count:
            _cards.extend(self.pool[:count])
            del self.pool[:count]
        else:
            _cards.extend(self.pool)
            self.pool.clear()
            self.shuffle(self.discard)
            self.pool = self.discard.copy()
            self.discard.clear()
            _cards.extend(self.draw(count - avail))
        return _cards

    @staticmethod
    def shuffle(pile):
        random.shuffle(pile)

    def score(self):
        points = sum([c.points for c in self if isinstance(c, cards.Victory) and isinstance(c.points, int)])
        points += sum([c.points(self) for c in self if isinstance(c, cards.Victory) and isinstance(c.points, function)])

    def __iter__(self):
        return self.discard + self.pool

    def __len__(self):
        return len(self.discard) + len(self.pool)

class Hand:
    actions = 1
    buys = 1
    money = 0

    def __init__(self, table, deck):
        self.table = table
        self.deck = deck
        self.cards = self.deck.draw(5)

    def __repr__(self):
        return '\n'.join([str(c) for c in self.cards])

    def __iter__(self):
        for c in self.cards:
            yield c

    def __contains__(self, item):
        return True if item in [c.name for c in self] else False

    def total_money(self):
        return sum([card.value for card in self.show_treasures()]) + self.money

    def show_treasures(self, _max=np.inf, overpay=False):
        coins = []
        treasure = sorted([c for c in self.cards if isinstance(c, cards.Treasure)], key=lambda x: x.value, reverse=True)
        for card in treasure:
            if not overpay and sum([c.value for c in coins]) + card.value <= _max:
                coins.append(card)
            elif overpay:
                coins.append(card)
            if sum([c.value for c in coins]) >= _max:
                break
        if np.isfinite(_max) and sum([c.value for c in coins]) < _max:
            if not overpay:
                self.show_treasures(_max, overpay=True)
            else:
                raise cards.InsufficientFundsError
        return coins

    def discard_treasure(self, value):
        treasure = self.show_treasures(value)
        self.deck.discard.extend(treasure)
        self.cards = [i for i in self.cards if i not in treasure or treasure.remove(i)]

    def discard(self):
        self.deck.discard.extend(self.cards)
        self.deck.discard.extend(self.deck.played)
        self.deck.played = []
        self.cards = []

    def play(self, gen_cards):
        for c in gen_cards:
            print(c)
            card = cards.get(c)
            self.deck.played.append(card)
            self.cards.remove(card)
            card.play(self)
            for a in card.actions:
                getattr(card, a[0])(*a[1:])

    def buy(self, gen_cards):
        spent = 0
        for name in gen_cards:
            if not name:
                total = self.total_money()
                while total > 0 and self.buys > 0:
                    avail = [c for c in cards.all_cards if c.cost <= total and c.name in self.table.all().non_empty_piles()]
                    # Prevent buying victory card before turn 20
                    if self.table.turn < 20:
                        avail = [c for c in avail if not isinstance(c, cards.Victory)]
                    if not avail:
                        break
                    choice = self.deck.buy_pref(avail)
                    self.deck.discard.extend(self.table.draw(choice.name, 1))
                    total -= choice.cost
                    spent += choice.cost
                    self.buys -= 1
            else:
                drawn_card = self.table.draw(name, 1)[0]
                self.deck.discard.append(drawn_card)
                self.money -= drawn_card.cost
                spent += drawn_card.cost
                self.buys -= 1
        self.discard_treasure(spent)

    def trash(self, gen_cards):
        for c in gen_cards:
            card = cards.get(c)
            if not card:
                return cards.Fail
            self.deck.trash.append(card)
            self.cards.remove(card)
        return cards.Success
