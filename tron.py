import random
import sys


class Tron:
    '''
    Based on the work done by: /u/Azgurath & /u/mpaw975
    '''
    def __init__(self):
        self.draw = True
        self.loops = 100000

        # report metrics
        self.turn_three_tron = 0
        self.turn_three_karn = 0
        self.total_have_karn = 0
        self.total_turns = 0
        self.failed_to_tron = 0
        self.failed_starting_size = 0
        self.success_starting_size = 0
        self.turn_four_tron = 0

        # experimental settings
        # for testing optimal behaviour
        self.scry_for_second_piece = False
        self.map_for_second_piece = False

    def game(self):
        '''
        main logic for how the games are played out
        '''
        self.populate_deck()
        # Populate field
        field = []

        # Populate cards on bottom
        bottom = []

        # Populate starting hand
        starting_size = 7
        decided_on_hand = False
        hand = random.sample(self.deck, 7)
        have_tron = False

        # Mulligan
        # Keep if guarunteed tron
        # Keep if 6 cards or less and 2 or more tron pieces
        # Keep if 4 or less cards and 1 or more tron pieces
        while not decided_on_hand and starting_size > 0:
            # natural tron
            if all(x in hand for x in ['Mine', 'Tower', 'PP']):
                have_tron = True
                decided_on_hand = True

            # guarunteed tron
            elif (self.troncheck(hand) >= 2 and (
                    ('map' in hand) or
                    ('scry' in hand and 'star' in hand))):
                have_tron = True
                decided_on_hand = True

            # 2 pieces
            if starting_size <= 6 and not decided_on_hand:
                if self.troncheck(hand) >= 2:
                    decided_on_hand = True
                if any(x in hand for x in ('Tower', 'Mine', 'PP')):
                    if 'map' in hand or 'scry' in hand:
                        decided_on_hand = True
                    elif all(x in hand for x in ('stir', 'star')):
                        decided_on_hand = True

            # 1 piece
            if starting_size <= 4 and not decided_on_hand:
                if any(x in hand for x in ('Tower', 'Mine', 'PP')):
                    decided_on_hand = True

            # Mull to 3
            if starting_size <= 3 and not decided_on_hand:
                decided_on_hand = True

            # Mulligan
            if not decided_on_hand:
                starting_size -= 1
                hand = random.sample(self.deck, starting_size)

        # Take the cards in hand from the deck
        for card in hand:
            self.deck.remove(card)

        # Scry if mulliganed
        scry = starting_size < 7
        scry_bottom = True
        new_card = ''
        if scry and not have_tron:
            new_card = random.choice(self.deck)
            # Have two pieces, keep map or third piece
            if self.troncheck(hand) >= 2:
                if new_card in ('map', 'Tower', 'Mine', 'PP') and (
                        new_card not in hand):
                    scry_bottom = False
                if new_card == 'scry' and any(
                        x in hand for x in ['star', 'forest']):
                    scry_bottom = False
                if new_card == any(x in hand for x in ['star', 'forest']) and (
                        'scry' in hand):
                    scry_bottom = False
                if new_card == 'stir' and any(
                        x in hand for x in ['star', 'forest']):
                    scry_bottom = False

            if scry_bottom:
                self.deck.remove(new_card)
                bottom.append(new_card)
                new_card = ''

        # Main loop for turns!
        turn = 0
        tron = False
        while not tron:
            # increment turn counter
            turn += 1

            # initialize mana to 0
            mana = 0
            green = 0
            lands_played = 0

            # draw a card
            # if it's the first card after scrying
            if (self.draw and turn == 1) or (not self.draw and turn == 2):
                if new_card == '':
                    new_card = random.choice(self.deck)
                hand.append(new_card)
                self.deck.remove(new_card)

            # otherwise
            elif self.draw or turn != 1:
                new_card = random.choice(self.deck)
                hand.append(new_card)
                self.deck.remove(new_card)

            # tap lands for mana
            for card in field:
                if card in ('Mine', 'PP', 'Tower', 'gq', 'forest'):
                    if card == 'forest':
                        green += 1
                    mana += 1

            # on second turn, crack stars before playing land
            # in order to see if we find more pieces
            if turn == 2 and 'star' in field and mana > 0:
                field.remove('star')
                new_card = random.choice(self.deck)
                self.deck.remove(new_card)
                hand.append(new_card)
                green += 1

            # play a new tron land
            for card in hand:
                if card in ('Mine', 'PP', 'Tower') and (
                        card not in field) and lands_played == 0:
                    hand.remove(card)
                    field.append(card)
                    mana += 1
                    lands_played = 1

            # check if we have tron
            if 'PP' in field and 'Tower' in field and 'Mine' in field:
                tron = True

            # crack stars for green
            if 'star' in field:
                field.remove('star')
                new_card = random.choice(self.deck)
                self.deck.remove(new_card)
                hand.append(new_card)
                green += 1

            # if two tron pieces, use map or scrying
            if self.troncheck(hand, field) >= 2:
                # cast and use map if none is in field and you have enough mana
                if 'map' in hand and 'map' not in field and mana > 2:
                    hand.remove('map')
                    field.append('map')
                    mana -= 1
                # use map
                if 'map' in field and mana > 1:
                    self.use_map(hand, field)
                    mana -= 2
                # cast scrying
                if 'scry' in hand and mana > 1 and green > 0:
                    self.use_scry(hand, field)
                    mana -= 2
                    green -= 1
                # cast map
                if 'map' in hand and mana > 0:
                    hand.remove('map')
                    field.append('map')
                    mana -= 1

            did_something = True
            while mana > 0 and did_something:
                did_something = False
                search_effects = 0
                for card in hand:
                    if card in ('scry', 'map'):
                        search_effects += 1

                # if mana, cast stirrings
                if green > 0 and mana > 0 and 'stir' in hand:
                    # use stirrings
                    green -= 1
                    mana -= 1
                    self.use_stir(hand, field)
                    did_something = True
                    continue

                # test to see if you should fetch second piece
                # w/o a plan for the third
                if self.scry_for_second_piece or search_effects > 1:
                    if green > 0 and mana > 1 and 'scry' in hand:
                        self.use_scry(hand, field)
                        mana -= 2
                        green -= 1
                        did_something = True
                        continue

                if search_effects > 1:
                    if mana > 1 and 'map' in field:
                        self.use_map(hand, field)
                        mana -= 2
                        did_something = True
                    if mana > 0 and 'map' in hand:
                        hand.remove('map')
                        field.append('map')
                        mana -= 1
                        did_something = True
                        continue

                # cast star
                if 'star' in hand and mana > 0:
                    hand.remove('star')
                    field.append('star')
                    mana -= 1
                    did_something = True
                    continue

                # crack star
                if 'star' in field and mana > 0:
                    field.remove('star')
                    green += 1
                    new_card = random.choice(self.deck)
                    self.deck.remove(new_card)
                    hand.append(new_card)
                    did_something = True
                    continue

                # map for second piece as a last resort
                # if nothing else yielded results
                if self.map_for_second_piece or search_effects > 1:
                    if mana > 1 and 'map' in field:
                        self.use_map(hand, field)
                        mana -= 2
                        did_something = True
                    if mana > 0 and 'map' in hand:
                        hand.remove('map')
                        field.append('map')
                        mana -= 1
                        did_something = True
                    continue

            # play a new tron land
            if lands_played == 0:
                for card in hand:
                    if card in ('Mine', 'PP', 'Tower') and card not in field:
                        hand.remove(card)
                        field.append(card)
                        mana += 1
                        lands_played = 1
                        if self.troncheck(hand, field) >= 2:
                            if 'map' in field and mana > 1:
                                self.use_map(hand, field)
                                mana -= 2
                            if 'scry' in hand and green > 0 and mana > 1:
                                self.use_scry(hand, field)
                                green -= 1
                                mana -= 2
                            if 'map' in hand and mana > 0:
                                hand.remove('map')
                                field.append('map')
                                mana -= 1

                if lands_played == 0:
                    if 'forest' in hand:
                        hand.remove('forest')
                        field.append('forest')
                        mana += 1
                        green += 1
                        lands_played = 1
                    if 'gq' in hand:
                        hand.remove('gq')
                        field.append('gq')
                        mana += 1
                        lands_played = 1

                if 'stir' in hand and green > 0 and mana > 0:
                    self.use_stir(hand, field)
                    green -= 1
                    mana -= 1

                if 'star' in hand and mana > 0:
                    hand.remove('star')
                    field.append('star')
                    mana -= 1
            # end turn

        if turn == 3:
            self.turn_three_tron += 1
        elif turn == 4:
            self.turn_four_tron += 1

        if turn == 3 and 'Karn' in hand:
            self.turn_three_karn += 1

        if 'Karn' in hand:
            self.total_have_karn += 1

        if turn < 10:
            self.total_turns += turn
            self.success_starting_size += starting_size
        else:
            self.failed_to_tron += 1
            self.failed_starting_size += starting_size

    def report(self):
        avg_turns = self.total_turns / float(self.loops - self.failed_to_tron)
        failed_avg_size = self.failed_starting_size / float(self.failed_to_tron)
        avg_size = self.success_starting_size / float(self.loops - self.failed_to_tron)
        turn_four_tron = self.turn_four_tron / float(self.loops) * 100
        tot_t4_tron = (self.turn_three_tron + self.turn_four_tron) / float(self.loops) * 100
        t3_karn = self.turn_three_karn / float(self.loops) * 100
        have_karn = self.total_have_karn / float(self.loops) * 100
        tot_failed = self.failed_to_tron / float(self.loops) * 100

        self.output('\nOn the play:' if not self.draw else '\nOn the draw')
        self.output('-' * 70)
        self.output('Turn three tron: {:.2f}%'.format(
            self.turn_three_tron / float(self.loops) * 100))
        self.output('Turn four tron: {:.2f}% (tot incl t3: {:.2f}%)'.format(
            turn_four_tron, tot_t4_tron))
        self.output('Turn three Karn: {:.2f}%'.format(t3_karn))
        self.output('Average turn tron: {:.2f}'.format(avg_turns))
        self.output('Have Karn when tron is done: {:.2f}%'.format(have_karn))
        self.output('Failed to get tron by tun 10: {:.2f}%'.format(tot_failed))
        self.output('Average starting hand size: {:.2f}'.format(avg_size))
        self.output('Average starting hand size when' +
                    'failed to get tron: {:.2f}'.format(failed_avg_size))
        self.output('-' * 70)

    @staticmethod
    def output(*message):
        op = ' '.join(message)
        sys.stdout.write(f'{op}\n')

    def populate_deck(self):
        self.deck = [
            'Mine', 'Mine', 'Mine', 'Mine',
            'PP', 'PP', 'PP', 'PP',
            'Tower', 'Tower', 'Tower', 'Tower',
            'star', 'star', 'star', 'star',
            'star', 'star', 'star', 'star',
            'map', 'map', 'map', 'map',
            # 'scry', 'scry', 'scry', 'scry',
            'stir', 'stir', 'stir', 'stir',
            'forest', 'forest', 'forest',
            'forest', 'forest', 'gq', 'gq',
            'Karn', 'Karn', 'Karn', 'Karn'
        ]
        for x in range(60 - len(self.deck)):
            self.deck.append('dead')
        self.bottom = []

    def settings(self, args):
        if 'test' in args:
            self.scry_for_second_piece = True
            self.map_for_second_piece = True
        if 'otp' in args:
            self.draw = False
        for arg in args:
            try:
                loops = int(arg)
                self.loops = loops
            except Exception:
                pass

    @staticmethod
    def troncheck(listA=[], listB=[]):
        '''
        used to check hand, field or hand + field for tron pieces
        '''
        tp = 0
        for x in ('Mine', 'Tower', 'PP'):
            tp += 1 if x in listA + listB else 0
        return tp

    def use_map(self, hand, field):
        field.remove('map')
        self.deck.extend(self.bottom)
        self.bottom = []
        for card in ('Tower', 'Mine', 'PP'):
            if card not in hand and card not in field:
                try:
                    self.deck.remove(card)
                except ValueError:
                    print('Hand: {}'.format(hand))
                    print('Field: {}'.format(field))
                    print('Deck: {}'.format(self.deck))
                hand.append(card)

    def use_scry(self, hand, field):
        hand.remove('scry')
        self.deck.extend(self.bottom)
        self.bottom = []
        for card in ('Tower', 'Mine', 'PP'):
            if card not in hand and card not in field:
                try:
                    self.deck.remove(card)
                except Exception:
                    print('Oops...')
                hand.append(card)

    def use_stir(self, hand, field):
        hand.remove('stir')
        cards = random.sample(self.deck, 5)
        card_chosen = ''

        # Look for if we have guraunteed tron
        if self.troncheck(hand, field) >= 2:
            if(('map' in hand or 'map' in field) or
               (('star' in hand or 'star' in field) and
               ('scry' in hand))):
                # If so, take Karn or stars to dig.
                if 'Karn' in cards and card_chosen == '':
                    card_chosen = 'Karn'
                if 'star' in cards and card_chosen == '':
                    card_chosen = 'star'
                if 'forest' in cards and card_chosen == '':
                    card_chosen = 'forest'

        # If we don't have tron, get things to help us get it

        # Get new tron piece
        if self.troncheck(hand, field) != 3:
            for card in cards:
                if card in ('Tower', 'Mine', 'PP'):
                    if card not in field and (
                            card not in hand) and card_chosen == '':
                        card_chosen = card

        else:
            # Get map if we have two pieces in hand
            if self.troncheck(hand, field) >= 2 and (
                    'map' in cards) and card_chosen == '':
                card_chosen = 'map'

            # Get a star
            if 'star' in cards and card_chosen == '':
                card_chosen = 'star'

            # Get a forest
            if 'forest' in cards and card_chosen == '':
                card_chosen = 'forest'

            # Get any other land
            for card in cards:
                if card in {'Tower', 'Mine', 'PP', 'gq'} and (
                        card_chosen == ''):
                    card_chosen = card

        # Add chosen card to hand, remove other five from the deck.
        # Ideally these cards will be stored in a list and re-appended
        #   to the deck when a map or scrying is used.
        if card_chosen != '':
            hand.append(card_chosen)

        for card in cards:
            self.deck.remove(card)
            self.bottom.append(card)


def main(args):
    T = Tron()
    T.settings(args)
    for i in range(T.loops):
        T.game()
    T.report()


if __name__ == '__main__':
    main(sys.argv)
