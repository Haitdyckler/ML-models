import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank} {self.suit}"
    
    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'Ace':
            return 11
        else:
            return int(self.rank)

class Deck:
    suits = ['♥', '◆', '♣', '♠']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'Ace']
    
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self):
        return self.cards.pop() if self.cards else None

class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        self.cards.append(card)
    
    def value(self):
        total = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'Ace')
        
        while total > 21 and aces:
            total -= 10
            aces -= 1
        
        return total
    
    def has_soft_ace(self):
        """Check if hand has an ace counting as 11"""
        total = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'Ace')
        
        if aces == 0:
            return False
        
        # Check if we can count an ace as 11 without busting
        hard_total = total - (aces * 10)  # All aces as 1
        return (hard_total + 11) <= 21
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.value() == 21
    
    def is_bust(self):
        return self.value() > 21
    
    def can_split(self):
        """Check if hand can be split (two cards of same rank)"""
        if len(self.cards) != 2:
            return False
        # Check if both cards have the same value (not rank, so 10, J, Q, K all count as 10)
        return self.cards[0].value() == self.cards[1].value()
    
    def __str__(self):
        return ', '.join(str(card) for card in self.cards)

class BlackjackExpertSystem:
    """Rule-based expert system using optimal basic strategy"""
    
    @staticmethod
    def should_split(player_hand, dealer_upcard, balance, bet):
        """Determine if hand should be split based on basic strategy"""
        if not player_hand.can_split():
            return False
        
        # Check if player has enough money to split
        if balance < bet:
            return False
        
        card_rank = player_hand.cards[0].rank
        dealer_value = dealer_upcard.value()
        
        # Always split Aces and 8s
        if card_rank == 'Ace' or card_rank == '8':
            return True
        
        # Never split 10s, face cards, 4s, or 5s
        if card_rank in ['10', 'J', 'Q', 'K', '4', '5']:
            return False
        
        # Split 2s and 3s against dealer 2-7
        if card_rank in ['2', '3']:
            return dealer_value <= 7
        
        # Split 6s against dealer 2-6
        if card_rank == '6':
            return dealer_value <= 6
        
        # Split 7s against dealer 2-7
        if card_rank == '7':
            return dealer_value <= 7
        
        # Split 9s against dealer 2-9 except 7
        if card_rank == '9':
            return dealer_value != 7 and dealer_value <= 9
        
        return False
    
    @staticmethod
    def decide_action(player_hand, dealer_upcard, can_split=False, balance=0, bet=0):
        """
        Returns 'h' for hit, 's' for stand, or 'p' for split based on basic strategy
        """
        # Check for split first
        if can_split and BlackjackExpertSystem.should_split(player_hand, dealer_upcard, balance, bet):
            return 'p'
        
        player_value = player_hand.value()
        dealer_value = dealer_upcard.value()
        has_soft_ace = player_hand.has_soft_ace()
        
        # Soft hand strategy (hand with ace counting as 11)
        if has_soft_ace:
            return BlackjackExpertSystem._soft_hand_strategy(player_value, dealer_value)
        else:
            return BlackjackExpertSystem._hard_hand_strategy(player_value, dealer_value)
    
    @staticmethod
    def _hard_hand_strategy(player_value, dealer_value):
        """Strategy for hard hands (no soft ace)"""
        # Always stand on 17 or higher
        if player_value >= 17:
            return 's'
        
        # Always hit on 11 or lower
        if player_value <= 11:
            return 'h'
        
        # Player has 12
        if player_value == 12:
            if dealer_value in [4, 5, 6]:
                return 's'
            else:
                return 'h'
        
        # Player has 13-16
        if 13 <= player_value <= 16:
            if dealer_value <= 6:
                return 's'
            else:
                return 'h'
        
        return 's'
    
    @staticmethod
    def _soft_hand_strategy(player_value, dealer_value):
        """Strategy for soft hands (hand with ace counting as 11)"""
        # Soft 19 or higher - always stand
        if player_value >= 19:
            return 's'
        
        # Soft 18
        if player_value == 18:
            if dealer_value in [9, 10, 11]:
                return 'h'
            else:
                return 's'
        
        # Soft 17 or lower - always hit
        if player_value <= 17:
            return 'h'
        
        return 's'
    
    @staticmethod
    def get_reasoning(player_hand, dealer_upcard, action, can_split=False):
        """Explain the reasoning behind the decision"""
        player_value = player_hand.value()
        dealer_value = dealer_upcard.value()
        has_soft_ace = player_hand.has_soft_ace()
        hand_type = "soft" if has_soft_ace else "hard"
        
        reasons = []
        
        if action == 'p':
            reasons.append(f"Expert System Decision: SPLIT")
            card_rank = player_hand.cards[0].rank
            reasons.append(f"Analysis: Pair of {card_rank}s vs Dealer {dealer_value}")
            
            if card_rank == 'Ace':
                reasons.append("✓ Rule: Always split Aces")
            elif card_rank == '8':
                reasons.append("✓ Rule: Always split 8s")
            elif card_rank in ['2', '3']:
                reasons.append("✓ Rule: Split 2s/3s vs dealer 2-7")
            elif card_rank == '6':
                reasons.append("✓ Rule: Split 6s vs dealer 2-6")
            elif card_rank == '7':
                reasons.append("✓ Rule: Split 7s vs dealer 2-7")
            elif card_rank == '9':
                reasons.append("✓ Rule: Split 9s vs dealer 2-9 except 7")
        elif action == 'h':
            reasons.append(f"Expert System Decision: HIT")
            reasons.append(f"Analysis: {hand_type.capitalize()} {player_value} vs Dealer {dealer_value}")
        else:
            reasons.append(f"Expert System Decision: STAND")
            reasons.append(f"Analysis: {hand_type.capitalize()} {player_value} vs Dealer {dealer_value}")
        
        # Add specific reasoning for hit/stand
        if action in ['h', 's']:
            if has_soft_ace:
                if player_value >= 19:
                    reasons.append("✓ Rule: Always stand on soft 19+")
                elif player_value == 18:
                    if dealer_value in [9, 10, 11]:
                        reasons.append("✓ Rule: Hit soft 18 vs dealer 9/10/A")
                    else:
                        reasons.append("✓ Rule: Stand on soft 18 vs weak dealer card")
                else:
                    reasons.append("✓ Rule: Hit soft 17 or lower (can't bust)")
            else:
                if player_value >= 17:
                    reasons.append("✓ Rule: Always stand on hard 17+")
                elif player_value <= 11:
                    reasons.append("✓ Rule: Always hit on 11 or lower (can't bust)")
                elif player_value == 12:
                    if dealer_value in [4, 5, 6]:
                        reasons.append("✓ Rule: Stand on 12 vs dealer 4-6 (dealer likely busts)")
                    else:
                        reasons.append("✓ Rule: Hit 12 vs strong dealer card")
                elif 13 <= player_value <= 16:
                    if dealer_value <= 6:
                        reasons.append("✓ Rule: Stand on 13-16 vs dealer 2-6 (dealer likely busts)")
                    else:
                        reasons.append("✓ Rule: Hit 13-16 vs dealer 7+ (dealer likely makes hand)")
        
        return '\n'.join(reasons)

class BlackjackGame:
    def __init__(self, use_expert_system=False):
        self.deck = Deck()
        self.player_hands = []  # Now support multiple hands for splits
        self.dealer_hand = Hand()
        self.player_balance = 1000
        self.use_expert_system = use_expert_system
        self.expert = BlackjackExpertSystem()
    
    def reset_hands(self):
        self.player_hands = []
        self.dealer_hand = Hand()
        if len(self.deck.cards) < 20:
            print("\nShuffling new deck...")
            self.deck = Deck()
    
    def deal_initial_cards(self):
        player_hand = Hand()
        player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hands.append(player_hand)
    
    def show_hands(self, hide_dealer=True, hand_index=0):
        print(f"\nYour balance: ${self.player_balance}")
        
        if len(self.player_hands) > 1:
            for i, hand in enumerate(self.player_hands):
                marker = " ← CURRENT" if i == hand_index else ""
                print(f"\nHand {i+1}: {hand} (Value: {hand.value()}){marker}")
        else:
            print(f"\nYour hand: {self.player_hands[0]} (Value: {self.player_hands[0].value()})")
        
        if hide_dealer:
            print(f"Dealer's hand: {self.dealer_hand.cards[0]}, [Hidden]")
        else:
            print(f"Dealer's hand: {self.dealer_hand} (Value: {self.dealer_hand.value()})")
    
    def play_hand(self, hand, bet, hand_index=0, is_split_ace=False):
        """Play a single hand, returns True if didn't bust"""
        if len(self.player_hands) > 1:
            print(f"\n{'='*50}")
            print(f"PLAYING HAND {hand_index + 1}")
            print(f"{'='*50}")
        
        self.show_hands(hide_dealer=True, hand_index=hand_index)
        
        # If split aces, only get one card and can't hit
        if is_split_ace:
            card = self.deck.deal()
            hand.add_card(card)
            print(f"\nYou drew: {card}")
            print(f"Hand {hand_index + 1}: {hand} (Value: {hand.value()})")
            print("(Split Aces receive only one card)")
            return not hand.is_bust()
        
        # Check for split option (only on first decision)
        can_split = hand.can_split() and len(self.player_hands) < 4 and self.player_balance >= bet
        
        first_action = True
        while True:
            if self.use_expert_system:
                # Expert system makes the decision
                action = self.expert.decide_action(
                    hand, 
                    self.dealer_hand.cards[0], 
                    can_split=can_split and first_action,
                    balance=self.player_balance,
                    bet=bet
                )
                reasoning = self.expert.get_reasoning(
                    hand, 
                    self.dealer_hand.cards[0], 
                    action,
                    can_split=can_split and first_action
                )
                print(f"\n{reasoning}")
                
                # Pause so user can see the decision
                input("\nPress Enter to execute decision...")
                choice = action
            else:
                prompt = "\nWould you like to (h)it or (s)tand"
                if can_split and first_action:
                    prompt += " or s(p)lit"
                prompt += "? "
                choice = input(prompt).lower()
            
            if choice == 'p' and can_split and first_action:
                return 'split'
            elif choice == 'h':
                hand.add_card(self.deck.deal())
                print(f"\nYou drew: {hand.cards[-1]}")
                if len(self.player_hands) > 1:
                    print(f"Hand {hand_index + 1}: {hand} (Value: {hand.value()})")
                else:
                    print(f"Your hand: {hand} (Value: {hand.value()})")
                
                if hand.is_bust():
                    print("\nBUST! You went over 21!")
                    return False
                
                first_action = False
                can_split = False  # Can only split on first action
            elif choice == 's':
                return True
            else:
                if choice == 'p':
                    if not first_action:
                        print("Can only split on your first action.")
                    elif not can_split:
                        print("Cannot split this hand.")
                    else:
                        print("Invalid input.")
                else:
                    print("Invalid input. Please enter 'h', 's'" + (", or 'p'" if can_split and first_action else "") + ".")
    
    def split_hand(self, hand_index, bet):
        """Split a hand into two hands"""
        hand = self.player_hands[hand_index]
        
        # Check if it's a pair of aces
        is_ace_split = hand.cards[0].rank == 'Ace'
        
        # Create two new hands
        card1 = hand.cards[0]
        card2 = hand.cards[1]
        
        hand1 = Hand()
        hand1.add_card(card1)
        hand1.add_card(self.deck.deal())
        
        hand2 = Hand()
        hand2.add_card(card2)
        hand2.add_card(self.deck.deal())
        
        # Replace original hand with two new hands
        self.player_hands[hand_index] = hand1
        self.player_hands.insert(hand_index + 1, hand2)
        
        # Deduct additional bet
        self.player_balance -= bet
        
        print(f"\n✂️ Hand split! Additional ${bet} bet placed.")
        print(f"Hand 1: {hand1} (Value: {hand1.value()})")
        print(f"Hand 2: {hand2} (Value: {hand2.value()})")
        
        return is_ace_split
    
    def dealer_turn(self):
        print("\nDealer's turn...")
        self.show_hands(hide_dealer=False)
        
        while self.dealer_hand.value() < 17:
            input("\nPress Enter to continue...")
            card = self.deck.deal()
            self.dealer_hand.add_card(card)
            print(f"Dealer drew: {card}")
            print(f"Dealer's hand: {self.dealer_hand} (Value: {self.dealer_hand.value()})")
            
            if self.dealer_hand.is_bust():
                print("\nDealer BUST!")
                return False
        
        return True
    
    def determine_winner(self, hand, bet, hand_index=0):
        player_val = hand.value()
        dealer_val = self.dealer_hand.value()
        
        hand_label = f"Hand {hand_index + 1}" if len(self.player_hands) > 1 else "Hand"
        
        print(f"\n{hand_label}: {hand} (Value: {player_val})")
        
        if hand.is_blackjack() and not self.dealer_hand.is_blackjack() and len(self.player_hands) == 1:
            winnings = int(bet * 1.5)
            self.player_balance += winnings
            print(f"BLACKJACK! You win ${winnings}!")
        elif self.dealer_hand.is_blackjack() and not hand.is_blackjack():
            self.player_balance -= bet
            print(f"Dealer has Blackjack. You lose ${bet}.")
        elif player_val > dealer_val:
            self.player_balance += bet
            print(f"You win ${bet}!")
        elif player_val < dealer_val:
            self.player_balance -= bet
            print(f"Dealer wins. You lose ${bet}.")
        else:
            print("It's a tie! Your bet is returned.")
    
    def play_round(self):
        self.reset_hands()
        
        print("\n" + "="*50)
        print("NEW ROUND")
        print("="*50)
        
        # Automatic betting for expert system (fixed bet of $10)
        if self.use_expert_system:
            bet = min(10, self.player_balance)
            print(f"\nAuto-betting: ${bet}")
        else:
            while True:
                try:
                    bet = int(input(f"\nPlace your bet (Balance: ${self.player_balance}): $"))
                    if bet <= 0:
                        print("Bet must be positive.")
                    elif bet > self.player_balance:
                        print("Insufficient funds.")
                    else:
                        break
                except ValueError:
                    print("Please enter a valid number.")
        
        self.deal_initial_cards()
        self.show_hands()
        
        # Check for initial blackjack
        if self.player_hands[0].is_blackjack():
            print("\nBLACKJACK!")
            if not self.dealer_hand.is_blackjack():
                self.show_hands(hide_dealer=False)
                winnings = int(bet * 1.5)
                self.player_balance += winnings
                print(f"You win ${winnings}!")
            else:
                self.show_hands(hide_dealer=False)
                print("Dealer also has Blackjack. Push!")
            return
        
        # Play each hand
        hand_bets = [bet]
        i = 0
        while i < len(self.player_hands):
            hand = self.player_hands[i]
            current_bet = hand_bets[i]
            
            # Check if this is from a split of aces
            is_split_ace = (i > 0 and len(self.player_hands) > 1 and 
                          self.player_hands[i].cards[0].rank == 'Ace' and
                          len(self.player_hands[i].cards) == 2)
            
            result = self.play_hand(hand, current_bet, i, is_split_ace)
            
            if result == 'split':
                was_ace_split = self.split_hand(i, current_bet)
                hand_bets.insert(i + 1, current_bet)
                # Don't increment i, replay the first split hand
                continue
            elif not result:
                # Hand busted
                self.player_balance -= current_bet
                print(f"You lose ${current_bet}.")
            
            i += 1
        
        # Count non-busted hands
        active_hands = [hand for hand in self.player_hands if not hand.is_bust()]
        
        if not active_hands:
            print("\nAll hands busted!")
            return
        
        # Dealer's turn
        dealer_survives = self.dealer_turn()
        
        print("\n" + "="*50)
        print("FINAL RESULTS")
        print("="*50)
        self.show_hands(hide_dealer=False)
        print()
        
        # Determine winners for each non-busted hand
        for i, hand in enumerate(self.player_hands):
            if not hand.is_bust():
                if dealer_survives:
                    self.determine_winner(hand, hand_bets[i], i)
                else:
                    # Dealer busted, player wins
                    self.player_balance += hand_bets[i]
                    hand_label = f"Hand {i + 1}" if len(self.player_hands) > 1 else "Hand"
                    print(f"{hand_label}: You win ${hand_bets[i]}!")
    
    def play_n_rounds(self, n_rounds=10, show_details=True):
        """Play N rounds automatically with the expert system"""
        print(f"\n{'='*50}")
        print(f"PLAYING {n_rounds} ROUNDS AUTOMATICALLY")
        print(f"{'='*50}")
        print(f"Starting balance: ${self.player_balance}")
        
        starting_balance = self.player_balance
        rounds_played = 0
        wins = 0
        losses = 0
        pushes = 0
        
        for round_num in range(1, n_rounds + 1):
            if self.player_balance <= 0:
                print(f"\n💸 Out of money after {rounds_played} rounds!")
                break
            
            print(f"\n{'='*50}")
            print(f"ROUND {round_num}/{n_rounds}")
            print(f"{'='*50}")
            
            balance_before = self.player_balance
            self.play_round_silent(show_details)
            balance_after = self.player_balance
            
            rounds_played += 1
            
            if balance_after > balance_before:
                wins += 1
            elif balance_after < balance_before:
                losses += 1
            else:
                pushes += 1
            
            if show_details and round_num < n_rounds:
                input("\nPress Enter for next round...")
        
        # Show summary
        print(f"\n{'='*60}")
        print(f"SIMULATION COMPLETE - {rounds_played} ROUNDS PLAYED")
        print(f"{'='*60}")
        print(f"Starting balance: ${starting_balance}")
        print(f"Ending balance:   ${self.player_balance}")
        profit = self.player_balance - starting_balance
        print(f"Net profit/loss:  ${profit:+d}")
        print(f"\nWins:   {wins}")
        print(f"Losses: {losses}")
        print(f"Pushes: {pushes}")
        if rounds_played > 0:
            win_rate = (wins / rounds_played) * 100
            print(f"Win rate: {win_rate:.1f}%")
    
    def play_round_silent(self, show_details=True):
        """Play a round with optional detail display"""
        self.reset_hands()
        
        # Fixed bet of $10
        bet = min(10, self.player_balance)
        if show_details:
            print(f"\nAuto-betting: ${bet}")
        
        self.deal_initial_cards()
        if show_details:
            self.show_hands()
        
        # Check for initial blackjack
        if self.player_hands[0].is_blackjack():
            if show_details:
                print("\nBLACKJACK!")
            if not self.dealer_hand.is_blackjack():
                if show_details:
                    self.show_hands(hide_dealer=False)
                winnings = int(bet * 1.5)
                self.player_balance += winnings
                if show_details:
                    print(f"You win ${winnings}!")
            else:
                if show_details:
                    self.show_hands(hide_dealer=False)
                    print("Dealer also has Blackjack. Push!")
            return
        
        # Play each hand
        hand_bets = [bet]
        i = 0
        while i < len(self.player_hands):
            hand = self.player_hands[i]
            current_bet = hand_bets[i]
            
            # Check if this is from a split of aces
            is_split_ace = (i > 0 and len(self.player_hands) > 1 and 
                          self.player_hands[i].cards[0].rank == 'Ace' and
                          len(self.player_hands[i].cards) == 2)
            
            result = self.play_hand_silent(hand, current_bet, i, is_split_ace, show_details)
            
            if result == 'split':
                was_ace_split = self.split_hand(i, current_bet)
                hand_bets.insert(i + 1, current_bet)
                continue
            elif not result:
                self.player_balance -= current_bet
                if show_details:
                    print(f"You lose ${current_bet}.")
            
            i += 1
        
        # Count non-busted hands
        active_hands = [hand for hand in self.player_hands if not hand.is_bust()]
        
        if not active_hands:
            if show_details:
                print("\nAll hands busted!")
            return
        
        # Dealer's turn
        dealer_survives = self.dealer_turn_silent(show_details)
        
        if show_details:
            print("\n" + "="*50)
            print("FINAL RESULTS")
            print("="*50)
            self.show_hands(hide_dealer=False)
            print()
        
        # Determine winners for each non-busted hand
        for i, hand in enumerate(self.player_hands):
            if not hand.is_bust():
                if dealer_survives:
                    self.determine_winner_silent(hand, hand_bets[i], i, show_details)
                else:
                    self.player_balance += hand_bets[i]
                    if show_details:
                        hand_label = f"Hand {i + 1}" if len(self.player_hands) > 1 else "Hand"
                        print(f"{hand_label}: You win ${hand_bets[i]}!")
    
    def play_hand_silent(self, hand, bet, hand_index=0, is_split_ace=False, show_details=True):
        """Play a single hand silently, returns True if didn't bust"""
        if show_details and len(self.player_hands) > 1:
            print(f"\n{'='*50}")
            print(f"PLAYING HAND {hand_index + 1}")
            print(f"{'='*50}")
            self.show_hands(hide_dealer=True, hand_index=hand_index)
        
        # If split aces, only get one card and can't hit
        if is_split_ace:
            card = self.deck.deal()
            hand.add_card(card)
            if show_details:
                print(f"\nYou drew: {card}")
                print(f"Hand {hand_index + 1}: {hand} (Value: {hand.value()})")
                print("(Split Aces receive only one card)")
            return not hand.is_bust()
        
        # Check for split option
        can_split = hand.can_split() and len(self.player_hands) < 4 and self.player_balance >= bet
        
        first_action = True
        while True:
            action = self.expert.decide_action(
                hand, 
                self.dealer_hand.cards[0], 
                can_split=can_split and first_action,
                balance=self.player_balance,
                bet=bet
            )
            
            if show_details:
                reasoning = self.expert.get_reasoning(
                    hand, 
                    self.dealer_hand.cards[0], 
                    action,
                    can_split=can_split and first_action
                )
                print(f"\n{reasoning}")
            
            if action == 'p' and can_split and first_action:
                return 'split'
            elif action == 'h':
                hand.add_card(self.deck.deal())
                if show_details:
                    print(f"\nYou drew: {hand.cards[-1]}")
                    if len(self.player_hands) > 1:
                        print(f"Hand {hand_index + 1}: {hand} (Value: {hand.value()})")
                    else:
                        print(f"Your hand: {hand} (Value: {hand.value()})")
                
                if hand.is_bust():
                    if show_details:
                        print("\nBUST! You went over 21!")
                    return False
                
                first_action = False
                can_split = False
            elif action == 's':
                return True
    
    def dealer_turn_silent(self, show_details=True):
        """Dealer's turn with optional display"""
        if show_details:
            print("\nDealer's turn...")
            self.show_hands(hide_dealer=False)
        
        while self.dealer_hand.value() < 17:
            card = self.deck.deal()
            self.dealer_hand.add_card(card)
            if show_details:
                print(f"Dealer drew: {card}")
                print(f"Dealer's hand: {self.dealer_hand} (Value: {self.dealer_hand.value()})")
            
            if self.dealer_hand.is_bust():
                if show_details:
                    print("\nDealer BUST!")
                return False
        
        return True
    
    def determine_winner_silent(self, hand, bet, hand_index=0, show_details=True):
        """Determine winner with optional display"""
        player_val = hand.value()
        dealer_val = self.dealer_hand.value()
        
        hand_label = f"Hand {hand_index + 1}" if len(self.player_hands) > 1 else "Hand"
        
        if show_details:
            print(f"\n{hand_label}: {hand} (Value: {player_val})")
        
        if hand.is_blackjack() and not self.dealer_hand.is_blackjack() and len(self.player_hands) == 1:
            winnings = int(bet * 1.5)
            self.player_balance += winnings
            if show_details:
                print(f"BLACKJACK! You win ${winnings}!")
        elif self.dealer_hand.is_blackjack() and not hand.is_blackjack():
            self.player_balance -= bet
            if show_details:
                print(f"Dealer has Blackjack. You lose ${bet}.")
        elif player_val > dealer_val:
            self.player_balance += bet
            if show_details:
                print(f"You win ${bet}!")
        elif player_val < dealer_val:
            self.player_balance -= bet
            if show_details:
                print(f"Dealer wins. You lose ${bet}.")
        else:
            if show_details:
                print("It's a tie! Your bet is returned.")
    
    def play(self):
        print("="*50)
        print("♠️♥️  WELCOME TO BLACKJACK  ♣️♦️")
        print("="*50)
        
        if self.use_expert_system:
            print("\nEXPERT SYSTEM MODE ENABLED")
            print("The AI will play using optimal basic strategy!")
            print("-"*50)
            
            # Ask if they want to play multiple rounds
            while True:
                mode = input("\nPlay mode:\n1. Step-by-step (one round at a time)\n2. Auto-play 10 rounds\n3. Auto-play 100 rounds (summary only)\nSelect (1/2/3): ")
                if mode in ['1', '2', '3']:
                    break
                print("Please enter 1, 2, or 3")
            
            if mode == '2':
                self.play_n_rounds(10, show_details=True)
                return
            elif mode == '3':
                self.play_n_rounds(100, show_details=False)
                return
        
        while self.player_balance > 0:
            self.play_round()
            
            if self.player_balance <= 0:
                print("\nYou're out of money! Game Over.")
                break
            
            if self.use_expert_system:
                # Auto-continue in expert mode with a pause
                play_again = input("\nContinue to next round? (y/n): ").lower()
                if play_again != 'y':
                    break
            else:
                play_again = input("\nPlay another round? (y/n): ").lower()
                if play_again != 'y':
                    break
        
        print(f"\nThanks for playing! Final balance: ${self.player_balance}")

if __name__ == "__main__":
    print("="*50)
    print("BLACKJACK GAME MODE SELECTION")
    print("="*50)
    print("1. Manual Mode - You make all decisions")
    print("2. Expert System Mode - AI plays using optimal strategy")
    
    while True:
        choice = input("\nSelect mode (1 or 2): ")
        if choice == '1':
            game = BlackjackGame(use_expert_system=False)
            break
        elif choice == '2':
            game = BlackjackGame(use_expert_system=True)
            break
        else:
            print("Please enter 1 or 2")
    
    game.play()