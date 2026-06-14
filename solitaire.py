#!/usr/bin/env python3 

import secrets
from card_core import Card, Suit, Rank

class Deck:
    def __init__(self):
        #Generate a standard deck layout
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        
    def shuffle(self):
        """Fisher-Yates in-place shuffle"""
        for i in range(len(self.cards) -1, 0, -1):
            j = secrets.randbelow(i + 1)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]
            
    def draw(self) -> Card:
        """Pop from the end of the lsit"""
        if not self.cards:
            raise ValueError("The deck is empty.")
        return self.cards.pop()
        
    def __len__(self):
        return len(self.cards)

class Board:
    def __init__(self):
        # Generate containers for the gameboard
        self.stock = Deck()
        self.waste = []
        self.tableaus = [[] for _ in range(7)]
        self.foundations = [[] for _ in range(4)]
        self.stock.shuffle()
        self.initialize_board()
    
    def initialize_board(self):
        # Draws cards from the deck and places them on the tableaus
        for y in range(0, 7):
            for x in range(y, 7):
                card = self.stock.draw()
                if x == y:
                    card.is_facedown = False
                self.tableaus[x].append(card)
    
    # Obtain the top card of the foundation
    def get_foundation_top(self, index):
        pile = self.foundations[index]
        return pile[-1] if pile else ""
    
    # Obtain the longest tableau length to identify the loop range
    def get_longest_tableau(self):
        longest = 0
        
        for i in range(7):
            longest = len(self.tableaus[i]) if len(self.tableaus[i]) > longest else longest
            
        return longest
        
    def show_board(self):
        # Presents a CLI visualization of the current game state
        
        # create visualization of a card back if stock pile has cards
        stock_state = "XXX" if len(self.stock) > 0 else "" 
        waste_state = self.waste[len(self.waste)-1] if len(self.waste) > 0 else "" 
        
        spade_state = self.get_foundation_top(0)
        diamond_state = self.get_foundation_top(1)
        club_state = self.get_foundation_top(2)
        heart_state = self.get_foundation_top(3)
        
        print("") # Line padding
        print(f"[{stock_state:>4} ][{waste_state:>4} ]{' ' * 7}[{spade_state:>4} ][{diamond_state:>4} ][{club_state:>4} ][{heart_state:>4} ]")
        print(f"{len(self.stock):>5}{len(self.waste):>7}")
        print(f"{"  ---  " * 7}")
        
        for y in range(self.get_longest_tableau()):
            for x in range(7):
                if y < len(self.tableaus[x]):
                    value = f"[{self.tableaus[x][y]:>4} ]"
                else: 
                    value = " " * 7
                
                print(value, end="")
            print("")
        print("")
        
def main():
    game = Board()
    game.show_board()
    
main()