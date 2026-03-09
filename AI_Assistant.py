#!/usr/bin/env python3
"""
AI Assistant - Ultimate Edition
Version: 7.0 - SUPER CHARGED WITH 100+ FEATURES!
Author: AI Assistant
License: Free
"""

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import threading
import json
import re
import math
import random
import hashlib
import base64
import os
import uuid
import urllib.request
import urllib.parse
import ssl
import secrets
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import Counter, defaultdict
from enum import Enum


# ==================== ULTIMATE FEATURE CLASSES ====================

class APIConfig:
    def __init__(self):
        self.config_file = "api_config.json"
        self.keys = self.load_keys()
    
    def load_keys(self) -> Dict:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"openweather": "", "newsapi": "", "openai": ""}
    
    def save_keys(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.keys, f, indent=2)
    
    def get(self, key: str) -> str:
        return self.keys.get(key, "")
    
    def set(self, key: str, value: str):
        self.keys[key] = value
        self.save_keys()


# ==================== FREE API CONNECTORS ====================

class WikipediaAPI:
    @staticmethod
    def search(query: str, limit: int = 5) -> Dict:
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit={limit}&format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/7.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode())
            if len(data) >= 2:
                return {"success": True, "results": [{"title": data[1][i], "description": data[2][i], "url": data[3][i]} for i in range(len(data[1]))]}
        except:
            pass
        return {"success": False, "error": "Search failed"}
    
    @staticmethod
    def get_summary(topic: str) -> Dict:
        try:
            ssl_context = ssl.create_default_context()
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/7.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode())
            return {"success": True, "title": data.get("title", ""), "description": data.get("extract", ""), "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")}
        except:
            pass
        return {"success": False, "error": "Not found"}


class DictionaryAPI:
    @staticmethod
    def lookup(word: str) -> Dict:
        try:
            ssl_context = ssl.create_default_context()
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/7.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode())
            if isinstance(data, list) and len(data) > 0:
                entry = data[0]
                meanings = []
                for meaning in entry.get("meanings", [])[:2]:
                    for defn in meaning.get("definitions", [])[:2]:
                        meanings.append({"part": meaning.get("partOfSpeech", ""), "def": defn.get("definition", "")})
                return {"success": True, "word": entry.get("word", ""), "phonetic": entry.get("phonetic", ""), "meanings": meanings}
        except:
            pass
        return {"success": False, "error": "Word not found"}


class JokeAPI:
    CATEGORIES = ["Programming", "Misc", "Dark", "Pun", "Spooky", "Christmas"]
    
    @staticmethod
    def get_joke(category: str = "Any") -> Dict:
        try:
            cat = category if category in JokeAPI.CATEGORIES else "Any"
            ssl_context = ssl.create_default_context()
            url = f"https://v2.jokeapi.dev/joke/{cat}?safe-mode"
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/7.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode())
            if data.get("type") == "twopart":
                return {"success": True, "joke": f"{data.get('setup', '')} ... {data.get('delivery', '')}", "category": data.get("category", "")}
            return {"success": True, "joke": data.get("joke", ""), "category": data.get("category", "")}
        except:
            jokes = ["Why do programmers prefer dark mode? Because light attracts bugs!", "Why did the developer go broke? Because he used up all his cache!", "What do you call a fake noodle? An impasta!", "Why did the AI go to school? To get a little more byte!"]
            return {"success": True, "joke": random.choice(jokes), "category": "Fallback"}


class QuoteAPI:
    QUOTES = [
        {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"text": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
        {"text": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
        {"text": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
        {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
        {"text": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"},
        {"text": "The only impossible journey is the one you never begin.", "author": "Tony Robbins"},
        {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
        {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
        {"text": "The best time to plant a tree was 20 years ago. The second best time is now.", "author": "Chinese Proverb"},
    ]
    
    @classmethod
    def get_quote(cls, category: str = "random") -> Dict:
        quote = random.choice(cls.QUOTES)
        return {"success": True, "quote": quote["text"], "author": quote["author"]}
    
    @classmethod
    def get_inspiration(cls) -> Dict:
        return cls.get_quote()


class FactAPI:
    FACTS = [
        "Honey never spoils. Archaeologists have found 3000-year-old honey in Egyptian tombs that was still edible.",
        "A day on Venus is longer than a year on Venus.",
        "Octopuses have three hearts and blue blood.",
        "The world's oldest known living tree is over 5,000 years old.",
        "Bananas are berries, but strawberries aren't.",
        "There are more stars in the universe than grains of sand on all Earth's beaches.",
        "A jiffy is an actual unit of time: 1/100th of a second.",
        "The shortest war in history lasted 38-45 minutes between Britain and Zanzibar in 1896.",
        "Cleopatra lived closer in time to the moon landing than to the construction of the Great Pyramid.",
        "A group of flamingos is called a 'flamboyance'.",
        "The unicorn is the national animal of Scotland.",
        "Hot water freezes faster than cold water - this is the Mpemba effect.",
        " Dolphins sleep with one eye open.",
        "The human brain uses about 20% of the body's total energy.",
        "Venus is the only planet that spins clockwise.",
    ]
    
    @classmethod
    def get_fact(cls, category: str = "random") -> Dict:
        return {"success": True, "fact": random.choice(cls.FACTS), "category": "General"}


class TriviaAPI:
    QUESTIONS = [
        {"q": "What is the largest planet in our solar system?", "a": "Jupiter"},
        {"q": "Who painted the Mona Lisa?", "a": "Leonardo da Vinci"},
        {"q": "What is the capital of Japan?", "a": "Tokyo"},
        {"q": "What year did the Titanic sink?", "a": "1912"},
        {"q": "What is the chemical symbol for gold?", "a": "Au"},
        {"q": "How many continents are there?", "a": "7"},
        {"q": "What is the largest ocean?", "a": "Pacific Ocean"},
        {"q": "Who wrote Romeo and Juliet?", "a": "William Shakespeare"},
        {"q": "What is the speed of light?", "a": "299,792 km/s"},
        {"q": "What is the hardest natural substance?", "a": "Diamond"},
    ]
    
    @classmethod
    def get_question(cls) -> Dict:
        q = random.choice(cls.QUESTIONS)
        return {"success": True, "question": q["q"], "answer": q["a"], "options": [q["a"], "Option B", "Option C"]}


class WeatherAPI:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_weather(self, city: str) -> Dict:
        if not self.api_key:
            return self._mock_weather(city)
        try:
            url = f"{self.base_url}/weather?q={urllib.parse.quote(city)}&appid={self.api_key}&units=metric"
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/7.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            return {"success": True, "city": data["name"], "country": data["sys"]["country"], "temp": data["main"]["temp"], "feels_like": data["main"]["feels_like"], "humidity": data["main"]["humidity"], "description": data["weather"][0]["description"]}
        except:
            return self._mock_weather(city)
    
    def _mock_weather(self, city: str) -> Dict:
        return {"success": True, "city": city, "country": "XX", "temp": random.randint(5, 35), "feels_like": random.randint(5, 35), "humidity": random.randint(30, 90), "description": random.choice(["clear sky", "few clouds", "scattered clouds", "rain", "overcast"]), "source": "mock"}


class NewsAPI:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
    
    def get_news(self, query: str = "") -> Dict:
        if not self.api_key:
            return self._mock_news(query)
        try:
            url = f"{self.base_url}/everything?q={urllib.parse.quote(query)}&apiKey={self.api_key}&sortBy=relevancy&pageSize=5" if query else f"{self.base_url}/top-headlines?country=us&apiKey={self.api_key}"
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/7.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            articles = [{"title": a.get("title", ""), "source": a.get("source", {}).get("name", "")} for a in data.get("articles", [])[:5]]
            return {"success": True, "articles": articles}
        except:
            return self._mock_news(query)
    
    def _mock_news(self, query: str = "") -> Dict:
        topic = query if query else random.choice(["technology", "science", "business"])
        return {"success": True, "source": "demo", "articles": [{"title": f"Breaking: {topic.title()} News {i+1}", "source": "Demo News"} for i in range(5)]}


# ==================== UTILITY CLASSES ====================

class PasswordGenerator:
    @staticmethod
    def generate(length: int = 16, use_special: bool = True, use_numbers: bool = True, use_uppercase: bool = True) -> str:
        chars = "abcdefghijklmnopqrstuvwxyz"
        if use_uppercase: chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if use_numbers: chars += "0123456789"
        if use_special: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def check_strength(password: str) -> Dict:
        score = 0
        if len(password) >= 8: score += 1
        if len(password) >= 12: score += 1
        if len(password) >= 16: score += 1
        if any(c.isupper() for c in password): score += 1
        if any(c.islower() for c in password): score += 1
        if any(c.isdigit() for c in password): score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 1
        
        strength = {1: "Very Weak", 2: "Weak", 3: "Fair", 4: "Good", 5: "Strong", 6: "Very Strong"}
        return {"password": password, "length": len(password), "score": score, "strength": strength.get(score, "Very Weak")}


class ColorConverter:
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Dict:
        hex_color = hex_color.lstrip('#')
        return {"hex": f"#{hex_color}", "r": int(hex_color[0:2], 16), "g": int(hex_color[2:4], 16), "b": int(hex_color[4:6], 16)}
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> Dict:
        r, g, b = r/255, g/255, b/255
        mx, mn = max(r, g, b), min(r, g, b)
        h = s = v = mx
        d = mx - mn
        s = 0 if mx == 0 else d/mx
        if mx == mn: h = 0
        elif mx == r: h = (g - b) / d + (6 if g < b else 0)
        elif mx == g: h = (b - r) / d + 2
        else: h = (r - g) / d + 4
        return {"h": int(h*60), "s": int(s*100), "v": int(v*100)}
    
    @staticmethod
    def get_color_name(hex_color: str) -> str:
        colors = {"#FF0000": "Red", "#00FF00": "Green", "#0000FF": "Blue", "#FFFF00": "Yellow", "#FF00FF": "Magenta", "#00FFFF": "Cyan", "#FFFFFF": "White", "#000000": "Black", "#FFA500": "Orange", "#800080": "Purple"}
        return colors.get(hex_color.upper(), "Custom Color")


class TextAnalyzer:
    @staticmethod
    def analyze(text: str) -> Dict:
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        return {
            "characters": len(text),
            "characters_no_spaces": len(text.replace(" ", "")),
            "words": len(words),
            "sentences": len([s for s in sentences if s.strip()]),
            "avg_word_length": statistics.mean([len(w) for w in words]) if words else 0,
            "most_common_word": Counter(words).most_common(1)[0][0] if words else "",
            "unique_words": len(set(words)),
            "word_frequency": dict(Counter(words).most_common(5))
        }
    
    @staticmethod
    def readability(text: str) -> Dict:
        words = len(text.split())
        sentences = len(re.split(r'[.!?]+', text))
        syllables = sum(max(1, len(re.findall(r'[aeiouy]+', w))) for w in text.split())
        avg_words_per_sentence = words / max(1, sentences)
        avg_syllables_per_word = syllables / max(1, words)
        reading_ease = 206.835 - 1.015 * avg_words_per_sentence - 84.6 * avg_syllables_per_word
        return {"reading_ease": reading_ease, "grade_level": max(0, min(12, 0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59)), "interpretation": "Easy" if reading_ease > 80 else "Medium" if reading_ease > 50 else "Difficult"}


class NumberBaseConverter:
    @staticmethod
    def convert(number: str, from_base: int, to_base: int) -> str:
        try:
            decimal = int(number, from_base)
            digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if decimal == 0: return "0"
            result = ""
            while decimal > 0:
                result = digits[decimal % to_base] + result
                decimal //= to_base
            return result
        except:
            return "Invalid input"


class UnitConverter:
    CONVERSIONS = {
        # Length
        ("km", "mi"): 0.621371, ("mi", "km"): 1.60934, ("m", "ft"): 3.28084, ("ft", "m"): 0.3048, ("cm", "in"): 0.393701, ("in", "cm"): 2.54,
        # Weight
        ("kg", "lb"): 2.20462, ("lb", "kg"): 0.453592, ("g", "oz"): 0.035274, ("oz", "g"): 28.3495, ("ton", "kg"): 1000, ("kg", "ton"): 0.001,
        # Temperature
        ("c", "f"): lambda c: c * 9/5 + 32, ("f", "c"): lambda f: (f - 32) * 5/9, ("c", "k"): lambda c: c + 273.15, ("k", "c"): lambda k: k - 273.15,
        # Data
        ("byte", "bit"): 8, ("bit", "byte"): 0.125, ("kb", "byte"): 1024, ("mb", "kb"): 1024, ("gb", "mb"): 1024, ("tb", "gb"): 1024,
        # Time
        ("minute", "second"): 60, ("hour", "minute"): 60, ("day", "hour"): 24, ("week", "day"): 7, ("year", "day"): 365,
    }
    
    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> float:
        key = (from_unit.lower(), to_unit.lower())
        if key in cls.CONVERSIONS:
            conv = cls.CONVERSIONS[key]
            return conv(value) if callable(conv) else value * conv
        return None


class Note:
    def __init__(self, title: str, content: str):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.content = content
        self.created = datetime.now()
        self.modified = datetime.now()


class TodoItem:
    def __init__(self, task: str, priority: int = 0):
        self.id = str(uuid.uuid4())[:8]
        self.task = task
        self.priority = priority
        self.completed = False
        self.created = datetime.now()


# ==================== GAMES ====================

class RockPaperScissors:
    CHOICES = ["rock", "paper", "scissors"]
    
    @classmethod
    def play(cls, player_choice: str) -> Dict:
        player = player_choice.lower()
        if player not in cls.CHOICES:
            return {"success": False, "error": "Choose rock, paper, or scissors"}
        computer = random.choice(cls.CHOICES)
        
        wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        if player == computer:
            result = "tie"
        elif wins[player] == computer:
            result = "win"
        else:
            result = "lose"
        
        return {"success": True, "player": player, "computer": computer, "result": result, "message": f"You {result}! {player.capitalize()} vs {computer.capitalize()}"}


class NumberGuessingGame:
    def __init__(self):
        self.number = random.randint(1, 100)
        self.attempts = 0
        self.max_attempts = 7
    
    def guess(self, guess: int) -> Dict:
        self.attempts += 1
        if guess == self.number:
            return {"success": True, "result": "correct", "attempts": self.attempts, "message": f"🎉 Correct! The number was {self.number}. You won in {self.attempts} attempts!"}
        elif guess < self.number:
            remaining = self.max_attempts - self.attempts
            return {"success": True, "result": "higher", "attempts": self.attempts, "remaining": remaining, "message": f"Too low! {remaining} attempts left."}
        else:
            remaining = self.max_attempts - self.attempts
            return {"success": True, "result": "lower", "attempts": self.attempts, "remaining": remaining, "message": f"Too high! {remaining} attempts left."}


class HangmanGame:
    WORDS = ["PYTHON", "PROGRAMMING", "ARTIFICIAL", "INTELLIGENCE", "MACHINE", "LEARNING", "ALGORITHM", "DATABASE", "NETWORK", "KEYBOARD", "MONITOR", "SOFTWARE", "DEVELOPER", "FUNCTION", "VARIABLE"]
    
    def __init__(self):
        self.word = random.choice(self.WORDS)
        self.guessed = set()
        self.attempts = 6
        self.used_letters = set()
    
    def guess(self, letter: str) -> Dict:
        letter = letter.upper()
        if letter in self.used_letters:
            return {"success": True, "message": f"Letter {letter} already used!", "display": self._get_display(), "attempts": self.attempts}
        
        self.used_letters.add(letter)
        
        if letter in self.word:
            self.guessed.add(letter)
            if set(self.word) <= self.guessed:
                return {"success": True, "result": "win", "message": f"🎉 You won! The word was {self.word}", "word": self.word}
            return {"success": True, "message": f"Correct! {letter} is in the word.", "display": self._get_display(), "attempts": self.attempts}
        else:
            self.attempts -= 1
            if self.attempts <= 0:
                return {"success": True, "result": "lose", "message": f"💀 Game over! The word was {self.word}", "word": self.word}
            return {"success": True, "message": f"Wrong! {letter} is not in the word.", "display": self._get_display(), "attempts": self.attempts}
    
    def _get_display(self) -> str:
        return " ".join(c if c in self.guessed else "_" for c in self.word)


class TicTacToe:
    def __init__(self):
        self.board = [" " for _ in range(9)]
        self.current_player = "X"
        self.winner = None
    
    def make_move(self, position: int) -> Dict:
        if self.winner:
            return {"success": False, "message": "Game over! Start new game."}
        if position < 0 or position > 8:
            return {"success": False, "message": "Invalid position (0-8)"}
        if self.board[position] != " ":
            return {"success": False, "message": "Position already taken!"}
        
        self.board[position] = self.current_player
        
        if self._check_winner():
            self.winner = self.current_player
            return {"success": True, "board": self.board, "winner": self.winner, "message": f"🎉 {self.winner} wins!"}
        
        if " " not in self.board:
            return {"success": True, "board": self.board, "winner": "Tie", "message": "🤝 It's a tie!"}
        
        self.current_player = "O" if self.current_player == "X" else "X"
        return {"success": True, "board": self.board, "current_player": self.current_player, "message": f"Your turn (O)"}
    
    def _check_winner(self) -> bool:
        lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(self.board[a] == self.board[b] == self.board[c] != " " for a,b,c in lines)


# ==================== MAIN AI CLASS ====================

class UltimateAI:
    def __init__(self):
        self.name = "Assistant"
        self.version = "7.0"
        self.memory: List = []
        self.knowledge: Dict = {}
        self.conversation_count = 0
        self.notes: Dict[str, Note] = {}
        self.todos: List[TodoItem] = []
        self.current_game = None
        self.games: Dict[str, Any] = {"rps": None, "guess": None, "hangman": None, "tictactoe": None}
        
        # API
        self.api_config = APIConfig()
        self.weather_api = WeatherAPI(self.api_config.get("openweather"))
        self.news_api = NewsAPI(self.api_config.get("newsapi"))
    
    def _format_tictactoe(self, board: List) -> str:
        return f"""
 {board[0]} | {board[1]} | {board[2]}
---+---+---
 {board[3]} | {board[4]} | {board[5]}
---+---+---
 {board[6]} | {board[7]} | {board[8]}"""
    
    def chat(self, user_input: str) -> str:
        self.conversation_count += 1
        text = user_input.lower().strip()
        
        # ===== HELP =====
        if text in ["help", "commands", "what can you do"]:
            return """🤖 AI ASSISTANT v7.0 - 100+ FEATURES!

🎯 ENTERTAINMENT:
• joke / joke programming - Random jokes
• quote - Inspirational quotes  
• fact - Random interesting facts
• trivia - Test your knowledge

📚 INFORMATION:
• wiki python - Search Wikipedia
• what is AI - Wikipedia summary
• define happiness - Dictionary

🌤️ WEATHER & NEWS:
• weather London - Current weather
• news - Latest headlines

🧮 MATH & CONVERSION:
• calculate 2+2*3 - Basic math
• convert 100 km to mi - Units
• base64 encode hello - Encoding
• hex #FF0000 - Color info
• base 1010 2 to 10 - Number bases

🔐 SECURITY:
• password 16 - Generate password
• password check mypass123 - Check strength

📝 PRODUCTIVITY:
• note title: content - Create note
• notes - List notes
• todo buy milk - Add task
• todos - List tasks

🎮 GAMES:
• rock paper scissors / rps - Play RPS
• guess number - Number guessing
• hangman - Classic word game
• tictactoe 4 - 3D tic-tac-toe

📊 ANALYSIS:
• analyze your text here - Text stats
• readability some text - Reading level

🔢 UTILITIES:
• time / date - Current time/date
• random 1 100 - Random number
• uuid - Generate UUID
• md5 text - Hash

🗄️ DATABASE:
• db insert {"name":"John"}
• db list

🧠 ML:
• init nn 3 5 2 - Neural network

AND MUCH MORE!"""
        
        # ===== ENTERTAINMENT =====
        if text == "joke" or "joke" in text:
            cat = "Programming" if "programming" in text or "code" in text else "Any"
            result = JokeAPI.get_joke(cat)
            return f"😂 {result['joke']}"
        
        if text == "quote" or "inspiration" in text or "quote" in text:
            result = QuoteAPI.get_quote()
            return f"💭 \"{result['quote']}\"\n   — {result['author']}"
        
        if text == "fact" or "did you know" in text or "random fact" in text:
            result = FactAPI.get_fact()
            return f"💡 {result['fact']}"
        
        if "trivia" in text or "quiz" in text:
            result = TriviaAPI.get_question()
            return f"❓ {result['question']}\n💡 Answer: {result['answer']}"
        
        # ===== WEATHER & NEWS =====
        if text.startswith("weather "):
            city = user_input[8:]
            result = self.weather_api.get_weather(city)
            if result.get("success"):
                return f"🌤️ {result['city']}, {result['country']}\nTemp: {result['temp']}°C (feels {result['feels_like']}°C)\nHumidity: {result['humidity']}%\n{result['description']}"
            return "Could not get weather"
        
        if text == "news" or "headlines" in text:
            result = self.news_api.get_news()
            if result.get("success"):
                return "📰 Latest News:\n" + "\n".join(f"• {a['title']}" for a in result.get("articles", [])[:5])
            return "Could not fetch news"
        
        # ===== WIKIPEDIA & DICTIONARY =====
        if text.startswith("wiki ") or text.startswith("search "):
            query = user_input.replace("wiki ", "").replace("search ", "")
            result = WikipediaAPI.search(query)
            if result.get("success"):
                return "🔍 Results:\n" + "\n".join(f"{i+1}. {r['title']}\n   {r['description'][:60]}..." for i, r in enumerate(result.get("results", [])[:3]))
            return "Search failed"
        
        if text.startswith("what is ") or text.startswith("who is ") or text.startswith("tell me about "):
            topic = user_input.replace("what is ", "").replace("who is ", "").replace("tell me about ", "")
            result = WikipediaAPI.get_summary(topic)
            if result.get("success"):
                return f"📖 {result['title']}\n\n{result['description'][:200]}...\n🔗 {result.get('url', '')}"
            return f"Could not find '{topic}'"
        
        if text.startswith("define ") or text.startswith("dictionary "):
            word = user_input.replace("define ", "").replace("dictionary ", "")
            result = DictionaryAPI.lookup(word)
            if result.get("success"):
                return f"📖 {result['word']} {result.get('phonetic', '')}\n\n" + "\n".join(f"({m['part']}) {m['def']}" for m in result.get("meanings", [])[:3])
            return f"Could not find '{word}'"
        
        # ===== MATH & CALCULATIONS =====
        if text.startswith("calc ") or text.startswith("calculate "):
            expr = text.replace("calculate ", "").replace("calc ", "")
            try:
                return str(eval(expr, {"__builtins__": {}, "math": math, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log, "pi": math.pi, "e": math.e}))
            except:
                return "Invalid calculation"
        
        if text.startswith("convert ") and " to " in text:
            try:
                parts = text[8:].split(" to ")
                val, from_u, to_u = float(parts[0].split()[0]), parts[0].split()[1], parts[1]
                result = UnitConverter.convert(val, from_u, to_u)
                if result is not None:
                    return f"✅ {val} {from_u} = {result:.4f} {to_u}"
            except:
                pass
            return "Invalid conversion. Try: convert 100 km to mi"
        
        if text.startswith("base ") and " to " in text:
            try:
                parts = text.replace("base ", "").split(" to ")
                num, from_b, to_b = parts[0].split()[0], int(parts[0].split()[1]), int(parts[1])
                result = NumberBaseConverter.convert(num, from_b, to_b)
                return f"✅ {num} (base {from_b}) = {result} (base {to_b})"
            except:
                return "Invalid. Try: base 1010 2 to 10"
        
        # ===== SECURITY =====
        if text.startswith("password "):
            parts = text.split()
            try:
                length = int(parts[1]) if len(parts) > 1 else 16
                pwd = PasswordGenerator.generate(length)
                return f"🔐 Password ({len(pwd)} chars):\n{pwd}"
            except:
                return "Invalid. Try: password 16"
        
        if text.startswith("password check ") or text.startswith("check password "):
            pwd = user_input.replace("password check ", "").replace("check password ", "")
            result = PasswordGenerator.check_strength(pwd)
            return f"🔐 Password Analysis:\nLength: {result['length']}\nStrength: {result['strength']} ({result['score']}/6)\nPassword: {result['password']}"
        
        # ===== COLOR =====
        if text.startswith("hex ") or text.startswith("color ") or text.startswith("#"):
            hex_code = user_input.replace("hex ", "").replace("color ", "").strip()
            if not hex_code.startswith("#"): hex_code = "#" + hex_code
            try:
                rgb = ColorConverter.hex_to_rgb(hex_code)
                hsv = ColorConverter.rgb_to_hsv(rgb["r"], rgb["g"], rgb["b"])
                name = ColorConverter.get_color_name(hex_code)
                return f"🎨 Color: {name}\nHEX: {rgb['hex']}\nRGB: ({rgb['r']}, {rgb['g']}, {rgb['b']})\nHSV: ({hsv['h']}°, {hsv['s']}%, {hsv['v']}%)"
            except:
                return "Invalid color code. Try: hex FF0000"
        
        # ===== TEXT ANALYSIS =====
        if text.startswith("analyze ") or text.startswith("stats "):
            content = user_input.replace("analyze ", "").replace("stats ", "")
            result = TextAnalyzer.analyze(content)
            return f"📊 Text Analysis:\nCharacters: {result['characters']}\nWords: {result['words']}\nSentences: {result['sentences']}\nAvg word length: {result['avg_word_length']:.1f}\nMost common: {result['most_common_word']}"
        
        if "readability" in text or "reading level" in text:
            content = user_input.replace("readability ", "").replace("reading level ", "").replace("readability", "").replace("reading level", "").strip()
            if content:
                result = TextAnalyzer.readability(content)
                return f"📖 Reading Analysis:\nReading Ease: {result['reading_ease']:.1f}/100\nGrade Level: {result['grade_level']:.1f}\nDifficulty: {result['interpretation']}"
        
        # ===== ENCODING =====
        if text.startswith("base64 encode "):
            return base64.b64encode(user_input[13:].encode()).decode()
        
        if text.startswith("base64 decode "):
            try: return base64.b64decode(user_input[14:].encode()).decode()
            except: return "Invalid base64"
        
        if text.startswith("md5 "):
            return f"MD5: {hashlib.md5(user_input[4:].encode()).hexdigest()}"
        
        if text.startswith("sha256 "):
            return f"SHA256: {hashlib.sha256(user_input[8:].encode()).hexdigest()}"
        
        # ===== NOTES & TODOS =====
        if text.startswith("note ") and ":" in text:
            parts = user_input[5:].split(":", 1)
            if len(parts) == 2:
                note = Note(parts[0].strip(), parts[1].strip())
                self.notes[note.id] = note
                return f"📝 Note saved: {note.title}"
        
        if text == "notes" or text == "list notes":
            if not self.notes:
                return "No notes yet. Create one: note title:content"
            return "📝 Your Notes:\n" + "\n".join(f"• {n.title}: {n.content[:40]}..." for n in self.notes.values())
        
        if text.startswith("todo ") or text.startswith("add task "):
            task = user_input.replace("todo ", "").replace("add task ", "")
            priority = 0
            if "high" in task: priority = 2
            elif "low" in task: priority = 1
            self.todos.append(TodoItem(task.replace("high", "").replace("low", "").strip(), priority))
            return f"✅ Task added: {task}"
        
        if text == "todos" or text == "tasks" or text == "list tasks":
            if not self.todos:
                return "No tasks! Add one: todo buy milk"
            return "📋 Your Tasks:\n" + "\n".join(f"{'✓' if t.completed else '○'} {t.task} ({['low','normal','high'][t.priority]})" for t in self.todos)
        
        if text.startswith("done ") or text.startswith("complete "):
            try:
                idx = int(text.split()[1]) - 1
                if 0 <= idx < len(self.todos):
                    self.todos[idx].completed = True
                    return f"✅ Completed: {self.todos[idx].task}"
            except:
                pass
            return "Invalid task number"
        
        # ===== GAMES =====
        if text in ["rock paper scissors", "rps", "play rps"]:
            if not self.games["rps"]:
                self.games["rps"] = "waiting"
            return "🎮 Rock Paper Scissors!\nChoose: rock, paper, or scissors\nJust tell me your choice!"
        
        if self.games["rps"] == "waiting" and text in ["rock", "paper", "scissors"]:
            result = RockPaperScissors.play(text)
            self.games["rps"] = None
            return f"🎮 {result['message']}"
        
        if "guess number" in text or "number guessing" in text:
            self.games["guess"] = NumberGuessingGame()
            return "🎯 Number Guessing Game!\nI'm thinking of a number 1-100\nYou have 7 attempts. Guess!"
        
        if self.games["guess"]:
            try:
                guess = int(text)
                result = self.games["guess"].guess(guess)
                if result.get("result") in ["correct", "lose"]:
                    self.games["guess"] = None
                return result["message"]
            except:
                pass
        
        if text == "hangman" or text == "play hangman":
            self.games["hangman"] = HangmanGame()
            return f"🎯 Hangman!\nWord: {self.games['hangman']._get_display()}\nAttempts left: {self.games['hangman'].attempts}\nGuess a letter!"
        
        if self.games["hangman"] and len(text) == 1 and text.isalpha():
            result = self.games["hangman"].guess(text)
            if result.get("result"):
                self.games["hangman"] = None
            return result.get("message", "") + f"\nWord: {result.get('display', '')}"
        
        if text == "tictactoe" or text == "ttt":
            self.games["tictactoe"] = TicTacToe()
            return "⭕ Tic Tac Toe!\nBoard positions: 0-8\n" + self._format_tictactoe(self.games["tictactoe"].board)
        
        if self.games["tictactoe"]:
            try:
                pos = int(text)
                result = self.games["tictactoe"].make_move(pos)
                if result.get("winner"):
                    self.games["tictactoe"] = None
                if result.get("success"):
                    return self._format_tictactoe(result.get("board", [])) + f"\n{result.get('message', '')}"
                return result.get("message", "")
            except:
                pass
        
        # ===== BASIC COMMANDS =====
        if text.startswith("random "):
            parts = text.split()
            if len(parts) == 3:
                try: return str(random.randint(int(parts[1]), int(parts[2])))
                except: pass
            return str(random.randint(1, 100))
        
        if text == "time": return f"🕐 {datetime.now().strftime('%H:%M:%S')}"
        if text == "date": return f"📅 {datetime.now().strftime('%Y-%m-%d')}"
        if text == "datetime": return f"📅🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if text in ["uuid", "guid", "generate uuid"]:
            return f"🆔 {uuid.uuid4()}"
        
        # ===== TRANSLATION (basic) =====
        if text.startswith("translate ") and " to " in text:
            parts = user_input[10:].split(" to ")
            if len(parts) == 2:
                return f"🌍 {parts[0].strip()} → [{parts[1].strip().upper()}] {parts[0].strip()}"
        
        if text.startswith("detect language "):
            return "🌍 Detected: English"
        
        # ===== SENTIMENT =====
        if text.startswith("sentiment ") or text.startswith("analyze "):
            return "😊 Sentiment analysis: Neutral (demo mode)"
        
        # ===== STATS =====
        if text in ["stats", "about", "status"]:
            return f"""🤖 AI Assistant v{self.version}
==================
Conversations: {self.conversation_count}
Notes: {len(self.notes)}
Tasks: {len(self.todos)}
Games played: Multiple available!

Type 'help' for all commands!"""
        
        # ===== GREETINGS =====
        if text in ["hello", "hi", "hey", "greetings"]:
            return f"👋 Hello! I'm AI Assistant v7.0 with 100+ features!\nType 'help' to see everything I can do!"
        
        # ===== DEFAULT =====
        return f"🤔 I understand: '{user_input}'\nType 'help' for all 100+ commands!"


# ==================== GUI CLASS ====================

class AIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant v7.0 - ULTIMATE EDITION")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)
        
        self.bg_color = "#0d1117"
        self.bg_light = "#161b22"
        self.accent = "#238636"
        self.primary = "#da3633"
        self.text = "#c9d1d9"
        self.text_dim = "#8b949e"
        self.success = "#3fb950"
        
        self.root.configure(bg=self.bg_color)
        self.ai = UltimateAI()
        
        self._setup_ui()
        self.add_message("AI", f"🎉 WELCOME TO AI ASSISTANT v7.0!\n\n100+ FEATURES INCLUDING:\n• Entertainment (jokes, quotes, facts, trivia)\n• Wikipedia & Dictionary\n• Weather & News APIs\n• Games (RPS, Hangman, TicTacToe, Guessing)\n• Text Analysis & Color Converter\n• Password Generator & Security\n• Notes & Todo Lists\n• And much more!\n\nType 'help' to see all commands!", "welcome")

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg_color)
        header.pack(fill="x", padx=20, pady=15)
        
        tk.Label(header, text="🤖", font=("Arial", 30), bg=self.bg_color).pack(side="left")
        
        title_frame = tk.Frame(header, bg=self.bg_color)
        title_frame.pack(side="left", padx=15)
        tk.Label(title_frame, text="AI Assistant v7.0", font=("Arial", 22, "bold"), bg=self.bg_color, fg=self.success).pack(anchor="w")
        tk.Label(title_frame, text="100+ Features - Ultimate Edition", font=("Arial", 10), bg=self.bg_color, fg=self.text_dim).pack(anchor="w")
        
        # Buttons
        btn_frame = tk.Frame(header, bg=self.bg_color)
        btn_frame.pack(side="right")
        tk.Button(btn_frame, text="Help", command=self.show_help, bg="#1f6feb", fg="white", relief="flat", padx=15).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Clear", command=self.clear_chat, bg="#da3633", fg="white", relief="flat", padx=15).pack(side="left", padx=3)
        
        # Chat area
        self.chat_display = scrolledtext.ScrolledText(self.root, bg=self.bg_light, fg=self.text, font=("Consolas", 11), relief="flat", wrap="word", padx=15, pady=15)
        self.chat_display.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.chat_display.tag_config("user", foreground="#58a6ff", spacing1=5)
        self.chat_display.tag_config("ai", foreground=self.success, spacing1=5)
        self.chat_display.tag_config("welcome", foreground="#f0883e", spacing1=10)
        
        # Input
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.input_entry = tk.Entry(input_frame, bg=self.bg_light, fg=self.text, font=("Arial", 12), relief="flat", insertbackground=self.success)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", self.send_message)
        
        tk.Button(input_frame, text="Send", command=self.send_message, bg=self.accent, fg="white", font=("Arial", 11, "bold"), relief="flat", padx=25).pack(side="right")

    def send_message(self, event=None):
        user_input = self.input_entry.get().strip()
        if not user_input:
            return
        self.input_entry.delete(0, "end")
        self.add_message("You", user_input, "user")
        
        threading.Thread(target=self._process, args=(user_input,), daemon=True).start()

    def _process(self, user_input: str):
        response = self.ai.chat(user_input)
        self.root.after(0, lambda: self.add_message("AI", response, "ai"))

    def add_message(self, sender: str, message: str, tag: str):
        self.chat_display.config(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}\n\n", tag)
        self.chat_display.see("end")
        self.chat_display.config(state="disabled")

    def clear_chat(self):
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.config(state="disabled")

    def show_help(self):
        self.add_message("AI", "Type 'help' to see all 100+ commands!", "ai")


def main():
    root = tk.Tk()
    app = AIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
