#!/usr/bin/env python3

from dataclasses import dataclass
from enum import Enum

class Suit(Enum):
    SPADES = ('♠', 'S', 1) 
    DIAMONDS = ('♦', 'D', 2)
    CLUBS = ('♣', 'C', 3)
    HEARTS = ('♥', 'H', 4)
    
    def __init__(self, symbol, suit_text, weight):
        self.symbol = symbol
        self.suit_text = suit_text
        self.weight = weight
        
    @classmethod
    def is_valid(cls, item):
        return any(item in (member.symbol, member.suit_text) for member in cls)
            
    @classmethod
    def return_symbol(cls, item):
        return next((m for m in cls if item in m.value), None)

class Rank(Enum):
    ACE = ('A', 1)
    TWO = ('2', 2)
    THREE = ('3', 3)
    FOUR = ('4', 4)
    FIVE = ('5', 5)
    SIX = ('6', 6)
    SEVEN = ('7', 7)
    EIGHT = ('8', 8)
    NINE = ('9', 9)
    TEN = ('10', 10)
    JACK = ('J', 11)
    QUEEN = ('Q', 12)
    KING = ('K', 13)
    
    @classmethod
    def is_valid(cls, item):
        return any(item in member.value for member in cls)
    
    @classmethod
    def return_weight(cls, item):
        rank_data = next((m for m in cls if item in m.value), None)
        if rank_data is not None:
            return rank_data.weight
        return rank_data
    
    @classmethod
    def return_symbol(cls, symbol_text):
        """Loops through all ranks and matches the input string to self.symbol."""
        return next((r for r in cls if symbol_text == r.symbol), None)

    def __init__ (self, symbol, weight):
        self.symbol = symbol
        self.weight = weight
    
# The cards used in game
@dataclass
class Card:
    rank: Optional[Rank] = None
    suit: Optional[Suit] = None
    is_facedown: bool = True
    is_joker: bool = False

    def __str__(self):
        if self.is_facedown:
            return f"XXX"
        if self.is_joker:
            return f"JKR"
        return f"{self.rank.symbol:>2}{self.suit.symbol}"
    
    def __format__(self, format_spec):
        return format(str(self), format_spec)
        
    def __repr__(self):
        if self.is_joker:
            return "Card(is_joker=True)"
        return f"Card(rank='{self.rank.name}' suit='{self.suit.name}')"


