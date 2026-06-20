#!/usr/bin/env python3 

import re
import sys
import secrets
from pathlib import Path
from card_core import Card, Suit, Rank
import json

class Deck:
    def __init__(self):
        #Generate a standard deck layout
        self.cards = []
    
    def __iter__(self):
        return iter(self.cards)
    
    def add_standard_deck(self):
        self.cards.extend(Card(rank, suit) for suit in Suit for rank in Rank)
        
    def shuffle(self):
        """Fisher-Yates in-place shuffle"""
        for i in range(len(self.cards) -1, 0, -1):
            j = secrets.randbelow(i + 1)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]
    
    def add(self, card):
        self.cards.append(card)
    
    def show_card(self, index = None):
        if index is None:
            index = len(self) - 1
        if not self.cards:
            return None
        else:
            return self.cards[index]
        
    def draw(self) -> Card:
        """Pop from the end of the list"""
        if not self.cards:
            return None
        else:
            return self.cards.pop()
        
    def __len__(self):
        return len(self.cards)
    
    def __bool__(self):
        return len(self.cards) > 0
        
class Board:
    def __init__(self):
        # Generate containers for the gameboard
        self.initialize_decks()
    
    def initialize_decks(self):
        # Create new deck objects for game containers
        self.stock = Deck()
        self.waste = Deck()
        self.tableaus = [Deck() for _ in range(7)]
        self.foundations = [Deck() for _ in range(4)]

    def initialize_board(self):
        self.stock.add_standard_deck()
        self.stock.shuffle()
        # Draws cards from the deck and places them on the tableaus
        for y in range(0, 7):
            for x in range(y, 7):
                card = self.stock.draw()
                if x == y:
                    card.is_facedown = False
                self.tableaus[x].add(card)
       
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
        
        spade_state = self.foundations[0].show_card() if self.foundations[0].show_card() is not None else ""
        diamond_state = self.foundations[1].show_card() if self.foundations[1].show_card() is not None else ""
        club_state = self.foundations[2].show_card() if self.foundations[2].show_card() is not None else ""
        heart_state = self.foundations[3].show_card() if self.foundations[3].show_card() is not None else ""
        
        print("") # Line padding
        self.show_waste()
        print(f"[{stock_state:>4} ][{waste_state:>4} ]{' ' * 7}[{spade_state:>4} ][{diamond_state:>4} ][{club_state:>4} ][{heart_state:>4} ]")
        print(f"{len(self.stock):>5}{len(self.waste):>7}")
        print("".join([f"  -{x}-  " for x in range(1,8)]))
        
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
            try:
                print(f"Input 'commands' to show list of commands")
                command = input("Command: ")
                split_string = command.strip().split(" ")
            
                option = split_string[0].upper()
                if option in ["MOVE", "M"]:
                    self.attempt_move(split_string[1].upper(), split_string [2:])
                elif option == ["COMMANDS", "C"]:
                    self.show_commands()
                elif option == "DRAW" or option == "D":
                    self.game_draw(3)
                elif option in ["SAVE", "S"]:
                    self.save_game(split_string[1])
                elif option in ["LOAD", "L"]:
                    self.load_game(split_string[1])
                elif option in ["QUIT"]:
                    return
                elif option in ["EXIT"]:
                    sys.exit(0)
                else:
                    print(f"Invalid Input")
            except IndexError:
                print(f"Invalid Input")
                
            exit = self.check_win()
     
    def clean_filename(self, filename):
        """ Check if filename is valid"""
        pattern = r'[<>:"/\\|?*]'

        return False if re.search(filename, pattern) else True    
        
    def save_game(self, filename = ""):
        """ Check if filename exists and confirm overwrite"""
        print(f"Saving Game...")
        filepath = Path.cwd() / "saves"

        filepath.mkdir(parents=True, exist_ok=True)

        if filename == "" or not self.clean_filename(filename):
            print("Invalid filename")
        else:
            filepath = (filepath / f"{filename}.json")
            if filepath.exists():
                confirmation = input("File already exists. Overwrite? Y-yes: ")
                if confirmation in ['Y', "y"]:
                    self.save_data(filepath)
            else:
                self.save_data(filepath)

    def save_data(self, filepath):
        """ Save card data to dictionary to put into JSON file """
        data = {"stock": [(card.rank.symbol,card.suit.suit_text) for card in self.stock], 
            "waste": [(card.rank.symbol,card.suit.suit_text) for card in self.waste],
            "foundations": [[(card.rank.symbol,card.suit.suit_text) for card in deck] for deck in self.foundations],
            "tableaus": [[(card.rank.symbol,card.suit.suit_text) for card in deck] for deck in self.tableaus]}
        
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            input("\nSave Complete, press Enter to continue")

    def check_win(self):
        """ Check if all the cards are in the foundations """
        done = True
        for foundation in self.foundations:
            done = False if (len(foundation) < 13) else True
            
        if done:
            print(f"----------   You Win!   ----------")
            return done
        return done
        
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
            if not self.stock:
                return
            card = self.stock.draw()
            card.is_facedown = False
            self.waste.add(card)
    
    def find_card_and_pile(self, target_card: Card):
        """Scans the baord and returns (source_deck, card_index) if found. """
        # Check waste pile (only the top card is playable)
        
        if self.waste.cards:
            top_waste_card = self.waste.cards[-1]
            if top_waste_card.rank == target_card.rank and top_waste_card.suit == target_card.suit:
                return self.waste, len(self.waste.cards) - 1
            
        # Check tableau columns (can move a card from the middle if face-up)
        for tableau in self.tableaus:
            for idx, card in enumerate(tableau.cards):
                    if card.rank == target_card.rank and card.suit == target_card.suit and not card.is_facedown:
                        return tableau, idx
                        
        return None, -1
    
    def tableau_move_valid(self, source, index, tableau):
        """ Passes user_card and tableau through serires of checks to see if movement is valid """
        suit_weight = {'S': 1, 'C': 1, 'D':0, 'H': 0}
        user_card = source.show_card(index)
        
        if (not tableau.isdigit()) or int(tableau) > 7 or int(tableau) < 1:
                    print(f"Invalid tableau")
                    return
        
        # Check if card is already in destination tableau
        if source is self.tableaus[int(tableau)-1]:
            print(f"Invaild Move: Card already in tableau")
            return
            
        # get card from the bottom of tableau
        tableau_card = self.tableaus[int(tableau)-1].show_card() #Adjust to zero-index
        # Compare card to move, with tableau card
        # Check if card is a K and the tableau is empty
        if not self.tableaus[int(tableau)-1]:
            if user_card.rank.symbol != "K":
                print(f"Invalid Move: Only a king can be moved into an empty tableau")
                return
        else:
            # check if card to move's value is directly below tableau card's value
            if user_card.rank.weight != tableau_card.rank.weight - 1:
                print(f"Invalid Move: Card value Incompaitble: {user_card.rank.weight} {tableau_card.rank.weight}")
                return
            # Check if suit is alternating via "colors". Diamond and Hearts are Red while Clubs and Spades are Black
            if suit_weight[user_card.suit.suit_text] == suit_weight[tableau_card.suit.suit_text]:
                print(f"Invalid Move: Suit Incompatible: {user_card.suit.symbol} {tableau_card.suit.symbol}")
                return
        
        self.move_cards(source, index, int(tableau) -1)
    
    def foundation_move_valid(self, source, index):
        
        # Obtain card to move
        user_card = source.show_card(index)
        
        # Obtain suit for locate suit foundation index
        suit_index = user_card.suit.weight - 1
        foundation = self.foundations[suit_index]
        
        # Check if foundation is empty card is not Ace
        if len(foundation) == 0:
            if user_card.rank.symbol != "A":
                print(f"Invalid Move: Only an Ace can be moved into an empty foundation")
                return
        else:
            # Check if card to move is the next card in sequence
            foundation_card = foundation.show_card()
            if user_card.rank.weight != foundation_card.rank.weight + 1:
                print(f"Invalid Move: Card not next in Sequence")
                return
        
        self.move_cards(source, index)        
        
    def attempt_move(self, card_str, destination):
        """Accepts a card_str from the command and checks if the card is currently available for movement. 
            Then checks if movement is valid and if true proceeds to move card and associated cards to the tableau"""
        valid = True

        tableau = None if not destination else destination[-1]

        suit = card_str[-1]
        rank = card_str[0:len(card_str)-1]
        
        matched_suit = Suit.return_symbol(suit)
        matched_rank = Rank.return_symbol(rank)
        
        if not matched_suit or not matched_rank:
            print(f"Invalid card")
            return
        else:
            user_card = Card(rank = matched_rank, suit = matched_suit, is_facedown=True)
            source, index = self.find_card_and_pile(user_card)
            
            if source is None:
                print(f"Cannot find Card")
                return
        if tableau is not None:
            self.tableau_move_valid(source, index, tableau)
        else:
            self.foundation_move_valid(source, index)

    def move_cards(self, source, index, tableau_index=None):
        """Once attempt_move has cleared all checks, move the card and connected cards to the new tableau"""
        placeholder_deck = Deck()
        for r in range(index, len(source)):
            placeholder_deck.add(source.draw())
        
        if tableau_index is not None:        
            while placeholder_deck:
                self.tableaus[tableau_index].add(placeholder_deck.draw())
        else:
            self.foundations[placeholder_deck.show_card().suit.weight - 1].add(placeholder_deck.draw())            
            
        self.post_move_cleanup(source)
     
    def post_move_cleanup(self, source_pile):
        """Flips the last card on the source tableau if there are cards"""
        if source_pile in self.tableaus and source_pile:
            source_pile.cards[-1].is_facedown = False
                
    def show_commands(self):
        """Shows the list of commands the user can use during gameplay"""
        print(f"\nCLI Klondike commands")
        print(f"Move 'card' to 'tableau #' - Move card and connected cards to tableau # or to foundation")
        print(f"    ex. Move 4S (4 of Spades) to 2")
        print(f"    ex. Move AS (Ace of Spades)")
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
        print(f"{"":<10}2 - Load Game")
        print(f"{"":<10}3 - Exit")
        option = input("Enter Input: ")  
        
        if option == "1":
            game = Board()
            game.initialize_board()
            game.game()
        elif option == "2":
            pass
        elif option == "3":
            exit = True
        
    
main()