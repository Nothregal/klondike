#!/usr/bin/env python3 

import sys
import secrets
from card_core import Card, Suit, Rank

class Deck:
    def __init__(self):
        #Generate a standard deck layout
        self.cards = []
    
    def add_standard_deck(self):
        self.cards.extend(Card(rank, suit) for suit in Suit for rank in Rank)
        
    def shuffle(self):
        """Fisher-Yates in-place shuffle"""
        for i in range(len(self.cards) -1, 0, -1):
            j = secrets.randbelow(i + 1)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]
    
    def add(self, card):
        self.cards.append(card)
    
    def show_card(self, index):
        return self.cards[index]
        
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
        self.stock.add_standard_deck()
        self.waste = Deck()
        self.tableaus = [Deck() for _ in range(7)]
        self.foundations = [Deck() for _ in range(4)]
        self.stock.shuffle()
        self.initialize_board()
    
    def initialize_board(self):
        # Draws cards from the deck and places them on the tableaus
        for y in range(0, 7):
            for x in range(y, 7):
                card = self.stock.draw()
                if x == y:
                    card.is_facedown = False
                self.tableaus[x].add(card)
    
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
        stock_state = self.stock.show_card(len(self.stock) - 1) if len(self.stock) > 0 else "" 
        waste_state = self.waste.show_card(len(self.waste) - 1) if len(self.waste) > 0 else "" 
        
        spade_state = self.get_foundation_top(0)
        diamond_state = self.get_foundation_top(1)
        club_state = self.get_foundation_top(2)
        heart_state = self.get_foundation_top(3)
        
        print("") # Line padding
        self.show_waste()
        print(f"[{stock_state:>4} ][{waste_state:>4} ]{' ' * 7}[{spade_state:>4} ][{diamond_state:>4} ][{club_state:>4} ][{heart_state:>4} ]")
        print(f"{len(self.stock):>5}{len(self.waste):>7}")
        print(f"{"  ---  " * 7}")
        
        for y in range(self.get_longest_tableau()):
            for x in range(7):
                if y < len(self.tableaus[x]):
                    value = f"[{self.tableaus[x].show_card(y):>4} ]"
                else: 
                    value = " " * 7
                
                print(value, end="")
            print("")
        print(f"{'-' * 30}")
    
    def game(self):
        """Main game method """
        exit = False
        
        while not exit:
            self.show_board()
            print(f"Input 'commands' to show list of commands")
            command = input("Command: ")
            
            option = command.lower().strip().split(" ")[0] #Obtain the first word of the string input
            if option == "commands":
                self.show_commands()
            if option == "draw":
                self.game_draw(3)
            if option == "quit":
                return
            if option == "exit":
                sys.exit(0)
    
    def show_waste(self):
        """Lists the cards in the waste pile in order of obtainability"""
        
        str_output = "Waste Cards: "
        for i in range(len(self.waste) - 1, -1, -1):
            str_output += " " if self.waste.show_card(i).rank.weight == 10 else "" 
            str_output += str(self.waste.show_card(i))
        print(f"{str_output}")
        
    def recycle(self):
        """Places all cards back to stock pile"""
        
        while self.waste:
            card = self.waste.draw()
            card.is_facedown = True
            self.stock.add(card)
            
    def game_draw(self, num_cards):
        """Draw # cards and places them on the waste pile in order of drawing. Automatically pulls cards back from waste pile the drawing if draw deck is empty"""
        
        if len (self.stock) == 0:
            self.recycle()
        
        for x in range(num_cards):
            card = self.stock.draw()
            card.is_facedown = False
            self.waste.add(card)
                
    def show_commands(self):
        """Shows the list of commands the user can use during gameplay"""
        print(f"\nCLI Klondike commands")
        print(f"Move 'card' to 'tableau #' - Move card and connected cards to tableau")
        print(f"    ex. Move 4S (4 of Spades) to 2")
        print(f"Raise 'card' - Move card to foundation")
        print(f"    ex. Raise AC (Ace of Clubs)")
        print(f"Draw - draws 3 cards from stock and places it on the waste")
        print(f"Save 'filename' - Saves current game to filename")
        print(f"Load 'filename' - Loads game from filename")
        print(f"Quit - Returns to Main Menu")
        print(f"Exit - Exits Program")
        input("\nPress Enter to Return to game")
        
def main():
    """Main menu for options and starting game"""
    
    exit = False
    
    while not exit:
        
        print(f"CLI Klondike Solitaire")
        print(f"{'-' * 30}")
        print(f"{"Options":<10}1 - New Game")
        print(f"{"":<10}2 - Exit")
        option = input("Enter Input: ")  
        
        if option == "1":
            game = Board()
            game.game()
        elif option == "2":
            exit = True
        
    
main()