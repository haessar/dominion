from unittest import TestCase

import board
import cards


class TestHand(TestCase):
    def setUp(self):
        self.table = board.Table()
        self.deck = board.Deck(self.table)
        self.treasure_hand = board.Hand(self.table, self.deck)
        self.treasures = [
            cards.get('gold'),
            cards.get('silver'),
            cards.get('copper'),
            cards.get('copper'),
            cards.get('copper'),
        ]
        self.treasure_hand.cards = self.treasures

    def test_show_treasures(self):
        self.assertListEqual(
            self.treasure_hand.show_treasures(7),
            [
                cards.get('gold'),
                cards.get('silver'),
                cards.get('copper'),
                cards.get('copper')
            ]
        )
        self.assertListEqual(
            self.treasure_hand.show_treasures(4),
            [
                cards.get('gold'),
                cards.get('copper')
            ]
        )
        self.assertListEqual(
            self.treasure_hand.show_treasures(4, overpay=True),
            [
                cards.get('gold'),
                cards.get('silver')
            ]
        )
        with self.assertRaises(cards.InsufficientFundsError):
            self.treasure_hand.show_treasures(9)

    def test_total_money(self):
        self.assertEqual(self.treasure_hand.total_money(), 8)

    def test_discard_treasure(self):
        self.treasure_hand.discard_treasure(4)
        self.assertListEqual(
            self.treasure_hand.cards,
            [
                cards.get('silver'),
                cards.get('copper'),
                cards.get('copper')
            ]
        )
        self.treasure_hand.cards = self.treasures
