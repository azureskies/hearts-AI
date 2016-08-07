"""This module containts the abstract class Player."""
from random import shuffle

from card import Suit, Rank, Deck


class Player:

    def pass_cards(self, hand):
        """Must return a list of three cards from the given hand."""
        return NotImplemented

    def play_card(self, hand, trick, are_hearts_broken):
        """Must return a card from the given hand."""
        return NotImplemented

    def is_card_valid(self, hand, trick, card, are_hearts_broken):
        """
        Return True if the given card is valid to play in given context, False otherwise.
        """
        if len(trick) == 0:
            return are_hearts_broken or (
                not are_hearts_broken and (card.suit != Suit.hearts
                                           or all([card.suit == Suit.hearts for card in hand]))
            )

        leading_suit = trick[0].suit
        return card.suit == leading_suit or all([card.suit != leading_suit for card in hand])


class StupidPlayer(Player):

    def pass_cards(self, hand):
        return hand[:3]

    def play_card(self, hand, trick, are_hearts_broken):
        # Play first card that is valid
        for card in hand:
            if self.is_card_valid(hand, trick, card, are_hearts_broken):
                return card
        raise AssertionError(
            'Apparently there is no valid card that can be played. This should not happen.'
        )


class SimplePlayer(Player):

    """
    This player has a notion of a card being undesirable.
    It will try to get rid of the most undesirable cards while trying not to win a trick.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        if verbose:
            deck = Deck()
            deck.cards.sort(key=self.undesirability)
            print('Card undesirability: ')
            for card in deck.cards:
                print('{}: {}'.format(card, self.undesirability(card)))

    def undesirability(self, card):
        return (
            card.rank.value
            + (10 if card.suit == Suit.spades and card.rank >= Rank.queen else 0)
        )

    def pass_cards(self, hand):
        hand.sort(key=self.undesirability, reverse=True)
        return hand[:3]

    def play_card(self, hand, trick, are_hearts_broken):
        # Lead with a low card
        if len(trick) == 0:
            hand.sort(key=lambda card: card.rank)
            return hand[0]

        hand.sort(key=self.undesirability, reverse=True)
        if self.verbose:
            print('Hand: {}'.format(hand))
            print('Trick so far: {}'.format(trick))

        # Safe cards are cards which will not result in winning the trick
        leading_suit = trick[0].suit
        max_rank_in_leading_suit = max([card.rank for card in trick
                                        if card.suit == leading_suit])
        valid_cards = [card for card in hand
                       if self.is_card_valid(hand, trick, card, are_hearts_broken)]
        safe_cards = [card for card in valid_cards
                      if card.suit != leading_suit or card.rank <= max_rank_in_leading_suit]

        if self.verbose:
            print('Valid cards: {}'.format(valid_cards))
            print('Safe cards: {}'.format(safe_cards))

        if safe_cards:
            return safe_cards[0]
        elif valid_cards:
            return valid_cards[0]

        raise AssertionError(
            'Apparently there is no valid card that can be played. This should not happen.'
        )
