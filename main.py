import cards
import board


def iter_action_response(hand):
    while hand.actions > 0 and any([c for c in hand if isinstance(c, cards.Action)]):
        print(hand)
        print('ACTIONS: {}'.format(hand.actions))
        resp = input('ACTIONS choice? (n to skip)')
        if resp == 'n':
            break
        else:
            if resp in hand:
                yield resp
            else:
                print('{} not a valid choice.'.format(resp))


def iter_buy_response(hand, table):
    while hand.buys > 0:
        print(hand)
        print('BUYS: {}'.format(hand.buys))
        print('MONEY: {}'.format(hand.total_money()))
        resp = input('BUYS choice? (n to skip, l for options)')
        if resp == 'n':
            break
        elif resp == 'l':
            print(table)
        else:
            if resp in table and cards.get(resp).cost <= hand.total_money():
                yield resp
            else:
                print('{} not a valid choice.'.format(resp))


def main(bots):

    table = board.Table()
    decks = {}

    player = board.Deck(table)
    for b in range(bots):
        decks['Bot {}'.format(b + 1)] = board.Deck(table)

    while True:
        table.turn += 1
        print('~~~~~~~~~    TABLE TURN: {}    ~~~~~~~~~'.format(table.turn))

        # Draw hand
        hand = board.Hand(table, player)
        # print(hand)

        # Action phase
        resp = iter_action_response(hand)
        hand.play(resp)

        # Buy phase
        resp = iter_buy_response(hand, table)
        hand.buy(resp)

        # End turn
        hand.discard()

        # Bots turns
        for deck in decks.values():
            hand = board.Hand(table, deck)
            hand.buy([''])
            hand.discard()

        if table.victories['province'] == 0 or len(table.all().empty_piles()) >= 3:
            print('Turn: {}'.format(table.turn))

            print('Player score: {}'.format(player.score()))
            for name, deck in decks.items():
                print('{} score: {}'.format(name, deck.score()))

            if player.score() > max([d.score() for _, d in decks.items()]):
                print('CONGRATULATIONS, YOU WIN!')
            else:
                print('YOU LOSE...')
            break


if __name__ == '__main__':
    main(bots=1)
