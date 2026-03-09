#!/usr/bin/env python3
"""
AI Assistant - Pro Edition v11
MAX FEATURES + Sleek UI
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
import json
import re
import math
import random
import os
import uuid
import urllib.request
import urllib.parse
import ssl
import secrets
import hashlib
import base64
import platform
from datetime import datetime, timedelta
from typing import Dict, List


# ==================== CONFIG ====================

class Config:
    def __init__(self):
        self.file = "config.json"
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"api_keys": {}, "user_name": "", "notes": [], "todos": []}
    
    def save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_key(self, name: str) -> str:
        return self.data.get("api_keys", {}).get(name, "")
    
    def set_key(self, name: str, key: str):
        if "api_keys" not in self.data:
            self.data["api_keys"] = {}
        self.data["api_keys"][name] = key
        self.save()
    
    def get_name(self) -> str:
        return self.data.get("user_name", "")
    
    def set_name(self, name: str):
        self.data["user_name"] = name
        self.save()
    
    def get_notes(self) -> List:
        return self.data.get("notes", [])
    
    def add_note(self, note: str):
        self.data.setdefault("notes", []).append({"text": note, "time": datetime.now().isoformat()})
        self.save()
    
    def get_todos(self) -> List:
        return self.data.get("todos", [])
    
    def add_todo(self, todo: str):
        self.data.setdefault("todos", []).append({"text": todo, "done": False, "time": datetime.now().isoformat()})
        self.save()
    
    def toggle_todo(self, index: int):
        todos = self.data.get("todos", [])
        if 0 <= index < len(todos):
            todos[index]["done"] = not todos[index]["done"]
            self.save()


# ==================== WEB APIS ====================

class WebAPIs:
    @staticmethod
    def fetch(url: str, timeout: int = 10) -> Dict:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent': 'AI-Pro/11'})
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                return {"success": True, "data": json.loads(resp.read().decode())}
        except:
            return {"success": False}
    
    @staticmethod
    def search_wikipedia(query: str) -> Dict:
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=5&format=json"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            data = result["data"]
            if len(data) >= 2:
                return {"success": True, "results": [{"title": data[1][i], "desc": data[2][i], "url": data[3][i]} for i in range(len(data[1]))]}
        return {"success": False}
    
    @staticmethod
    def get_wikipedia_summary(topic: str) -> Dict:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]
            return {"success": True, "title": d.get("title", ""), "text": d.get("extract", ""), "url": d.get("content_urls", {}).get("desktop", {}).get("page", "")}
        return {"success": False}
    
    @staticmethod
    def define_word(word: str) -> Dict:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            data = result["data"]
            if isinstance(data, list) and len(data) > 0:
                entry = data[0]
                defs = []
                for m in entry.get("meanings", [])[:2]:
                    for d in m.get("definitions", [])[:2]:
                        defs.append({"part": m.get("partOfSpeech", ""), "def": d.get("definition", "")[:120]})
                return {"success": True, "word": entry.get("word", ""), "phonetic": entry.get("phonetic", ""), "definitions": defs}
        return {"success": False}
    
    @staticmethod
    def get_weather(city: str, api_key: str = "") -> Dict:
        if not api_key:
            temps = [random.randint(5, 35) for _ in range(3)]
            return {"success": True, "city": city, "temp": temps[0], "feels": temps[1], "humidity": random.randint(30, 90), "desc": random.choice(["sunny", "cloudy", "rainy", "clear"]), "source": "demo"}
        url = f"https://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(city)}&appid={api_key}&units=metric"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]
            return {"success": True, "city": d["name"], "temp": d["main"]["temp"], "feels": d["main"]["feels_like"], "humidity": d["main"]["humidity"], "desc": d["weather"][0]["description"], "source": "live"}
        return {"success": False}
    
    @staticmethod
    def get_news(api_key: str = "", query: str = "") -> Dict:
        if not api_key:
            topics = ["Technology", "Science", "Business", "Sports", "Entertainment"]
            return {"success": True, "articles": [{"title": f"{random.choice(topics)} News {i+1}", "source": "Demo"} for i in range(5)]}
        url = f"https://newsapi.org/v2/{'top-headlines?country=us' if not query else 'everything?q=' + urllib.parse.quote(query)}&apiKey={api_key}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]
            return {"success": True, "articles": [{"title": a.get("title", ""), "source": a.get("source", {}).get("name", "")} for a in d.get("articles", [])[:5]]}
        return {"success": False}
    
    @staticmethod
    def get_ip_info() -> Dict:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request("https://ipapi.co/json/", headers={'User-Agent': 'AI-Pro/11'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                return {"success": True, "data": json.loads(resp.read().decode())}
        except:
            return {"success": False}


# ==================== KNOWLEDGE BASE ====================

class KnowledgeBase:
    def __init__(self):
        self.data = {
            "python": "Python - High-level programming language by Guido van Rossum (1991). Known for simplicity, readability, versatility. Used in web dev, data science, AI.",
            "javascript": "JavaScript - Web programming language. Runs in browsers and server-side with Node.js. Essential for interactive websites.",
            "ai": "Artificial Intelligence - Simulation of human intelligence in machines. Includes ML, NLP, computer vision, robotics.",
            "machine learning": "ML - Enables computers to learn from data without explicit programming. Includes supervised, unsupervised, reinforcement learning.",
            "deep learning": "Deep Learning - Neural networks with many layers. Powers image recognition, NLP, generative AI.",
            "chatgpt": "ChatGPT - AI chatbot by OpenAI, built on GPT-4. Answers questions, writes code, creates content.",
            "climate change": "Climate change - Long-term shifts in global temperatures. Caused by human activities like burning fossil fuels.",
            "universe": "Universe - Everything that exists: space, time, matter, energy. Created ~13.8 billion years ago in Big Bang.",
            "love": "Love - Complex emotional bond. Involves affection, care, respect, commitment. Essential for human well-being.",
            "health": "Health - Complete physical, mental, social well-being. Not just absence of disease. Key: diet, exercise, sleep.",
            "blockchain": "Blockchain - Distributed ledger technology. Records transactions across many computers. Secure, transparent.",
            "bitcoin": "Bitcoin - First cryptocurrency (2009). Decentralized digital money without banks. Uses blockchain.",
            "web3": "Web3 - Next internet evolution, built on blockchain. Includes dApps, NFTs, DeFi.",
            "quantum computing": "Quantum computing - Uses quantum mechanics to process information. Solves certain problems faster.",
            "spacex": "SpaceX - Space company by Elon Musk. Known for reusable rockets (Falcon 9, Starship) and Mars missions.",
            "elon musk": "Elon Musk - Tech entrepreneur. Founded SpaceX, Tesla, Neuralink, X. World's richest person.",
            "nasa": "NASA - US space agency. Founded 1958. Manages space exploration, ISS, Mars missions, Hubble.",
            "microsoft": "Microsoft - Tech giant founded by Bill Gates & Paul Allen (1975). Windows, Office, Azure, GitHub.",
            "apple": "Apple - Tech company by Steve Jobs & Steve Wozniak (1976). iPhone, Mac, iOS, App Store.",
            "google": "Google - Search engine by Larry Page & Sergey Brin (1998). Android, YouTube, Cloud services.",
            "amazon": "Amazon - E-commerce by Jeff Bezos (1994). AWS, Prime, Alexa.",
            "facebook": "Facebook - Social network by Mark Zuckerberg (2004). Now Meta. Instagram, WhatsApp.",
            "tesla": "Tesla - Electric car company by Elon Musk (2003). EVs, Solar, Powerwall, AI.",
            "nuclear energy": "Nuclear energy - Power from nuclear reactions. High energy density, low emissions. Concerns about waste.",
            "solar energy": "Solar energy - Energy from sunlight. Renewable, sustainable. Solar panels convert photons to electricity.",
            "wind energy": "Wind energy - Energy from wind. Renewable, sustainable. Wind turbines convert kinetic energy to electricity.",
        }
    
    def get(self, topic: str) -> str:
        topic = topic.lower().strip()
        if topic in self.data:
            return f"💡 {topic.title()}:\n\n{self.data[topic]}"
        for key, value in self.data.items():
            if key in topic or topic in key:
                return f"💡 {key.title()}:\n\n{value}"
        return None


# ==================== CURRENCY & CRYPTO ====================

class CurrencyConverter:
    RATES = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 149.5, "CNY": 7.24, "INR": 83.1, "CAD": 1.36, "AUD": 1.53, "CHF": 0.88, "BRL": 4.97, "KRW": 1320, "MXN": 17.15}
    
    @classmethod
    def convert(cls, amount: float, from_c: str, to_c: str) -> Dict:
        f, t = from_c.upper(), to_c.upper()
        if f in cls.RATES and t in cls.RATES:
            result = amount * cls.RATES[t] / cls.RATES[f]
            return {"success": True, "from": f, "to": t, "amount": amount, "result": round(result, 2)}
        return {"success": False}


class CryptoPrices:
    PRICES = {"BTC": 67500, "ETH": 3450, "XRP": 0.52, "ADA": 0.45, "DOGE": 0.12, "SOL": 145, "BNB": 580, "DOT": 7.2, "MATIC": 0.85, "LTC": 72}
    
    @classmethod
    def get_price(cls, coin: str) -> Dict:
        coin = coin.upper()
        if coin in cls.PRICES:
            return {"success": True, "coin": coin, "price": cls.PRICES[coin], "change": round(random.uniform(-5, 5), 2)}
        return {"success": False}


# ==================== ENTERTAINMENT ====================

class Entertainment:
    JOKES = [
        "Why do programmers hate nature? Too many bugs!",
        "Why did the developer go broke? Used up all his cache!",
        "What do you call a fake noodle? An impasta!",
        "Why do Java developers wear glasses? Because they can't C#!",
        "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?'",
        "Why did the AI break up with the blockchain? It needed more space!",
        "What's a programmer's favorite place? The Stack Overflow!",
        "Why do Python developers hate Java? Because it's strongly typed!",
        "What did the Python say to the JavaScript? You're so inconsistent!",
        "Why did the computer go to the doctor? Because it had a virus!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why can't you trust atoms? They make up everything!",
    ]
    
    FACTS = [
        "Honey never spoils - 3000-year-old honey found in Egyptian tombs was still edible!",
        "A day on Venus is longer than a year on Venus!",
        "Octopuses have three hearts and blue blood!",
        "Bananas are berries, but strawberries aren't!",
        "The world's oldest tree is over 5,000 years old!",
        "Hot water freezes faster than cold water (Mpemba effect)!",
        "The unicorn is Scotland's national animal!",
        "A group of flamingos is called a 'flamboyance'!",
        "Sharks are older than trees!",
        "A group of owls is called a 'parliament'!",
        "The shortest war in history lasted 38-45 minutes!",
        " Cleopatra lived closer to the moon landing than to the building of the Great Pyramid!",
    ]
    
    QUOTES = [
        ("The only way to do great work is to love what you do.", "Steve Jobs"),
        ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
        ("Stay hungry, stay foolish.", "Stewart Brand"),
        ("Life is what happens when you're busy making other plans.", "John Lennon"),
        ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
        ("Be the change you wish to see in the world.", "Mahatma Gandhi"),
        ("The greatest glory in living lies not in never falling, but in rising every time we fall.", "Nelson Mandela"),
        ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
    ]
    
    TRIVIA = [
        ("Largest planet?", "Jupiter"),
        ("Fastest animal?", "Cheetah"),
        ("Hardest substance?", "Diamond"),
        ("Largest ocean?", "Pacific"),
        ("Smallest country?", "Vatican City"),
        ("Tallest mountain?", "Mount Everest"),
        ("Longest river?", "Nile"),
        ("Largest mammal?", "Blue Whale"),
        ("Most spoken language?", "English"),
        ("Largest desert?", "Sahara"),
    ]
    
    RIDDLES = [
        ("What has keys but can't open locks?", "Piano"),
        ("What gets wetter the more it dries?", "Towel"),
        ("What can you catch but not throw?", "Cold"),
        ("What has a head and a tail but no body?", "Coin"),
        ("What comes once in a minute, twice in a moment, but never in a thousand years?", "M"),
    ]
    
    WOULD_YOU_RATHER = [
        ("Would you rather be able to fly or be invisible?", "Fly - think of the views!"),
        ("Would you rather have unlimited money or unlimited time?", "Money - time is precious!"),
        ("Would you rather live in the city or countryside?", "City - more energy!"),
        ("Would you rather be a famous actor or scientist?", "Scientist - change the world!"),
        ("Would you rather have super strength or super speed?", "Super speed - always on time!"),
    ]


# ==================== TEXT TOOLS ====================

class TextTools:
    @staticmethod
    def word_count(text: str) -> Dict:
        words = text.split()
        return {"words": len(words), "chars": len(text), "chars_no_spaces": len(text.replace(" ", "")), "lines": text.count("\n") + 1}
    
    @staticmethod
    def reverse_text(text: str) -> str:
        return text[::-1]
    
    @staticmethod
    def uppercase(text: str) -> str:
        return text.upper()
    
    @staticmethod
    def lowercase(text: str) -> str:
        return text.lower()
    
    @staticmethod
    def base64_encode(text: str) -> str:
        return base64.b64encode(text.encode()).decode()
    
    @staticmethod
    def base64_decode(text: str) -> str:
        try:
            return base64.b64decode(text.encode()).decode()
        except:
            return "Invalid Base64"
    
    @staticmethod
    def hash_md5(text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def hash_sha256(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()


# ==================== UNIT CONVERTER ====================

class UnitConverter:
    LENGTH = {"m": 1, "km": 1000, "cm": 0.01, "mm": 0.001, "mile": 1609.34, "yard": 0.9144, "foot": 0.3048, "inch": 0.0254}
    WEIGHT = {"kg": 1, "g": 0.001, "mg": 0.000001, "lb": 0.453592, "oz": 0.0283495, "ton": 1000}
    TEMP = {"c": "celsius", "f": "fahrenheit", "k": "kelvin"}
    
    @classmethod
    def convert_length(cls, value: float, from_u: str, to_u: str) -> float:
        f, t = from_u.lower(), to_u.lower()
        if f in cls.LENGTH and t in cls.LENGTH:
            return round(value * cls.LENGTH[f] / cls.LENGTH[t], 6)
        return None
    
    @classmethod
    def convert_weight(cls, value: float, from_u: str, to_u: str) -> float:
        f, t = from_u.lower(), to_u.lower()
        if f in cls.WEIGHT and t in cls.WEIGHT:
            return round(value * cls.WEIGHT[f] / cls.WEIGHT[t], 6)
        return None
    
    @classmethod
    def convert_temp(cls, value: float, from_u: str, to_u: str) -> float:
        f, t = from_u.lower(), to_u.lower()
        if f == "c":
            val = value
        elif f == "f":
            val = (value - 32) * 5/9
        elif f == "k":
            val = value - 273.15
        else:
            return None
        
        if t == "c":
            return round(val, 2)
        elif t == "f":
            return round(val * 9/5 + 32, 2)
        elif t == "k":
            return round(val + 273.15, 2)
        return None


# ==================== INTENT PARSER ====================

class IntentParser:
    @staticmethod
    def parse(text: str) -> Dict:
        t = text.lower().strip()
        
        if "?" in t or any(w in t for w in ["what", "who", "where", "when", "why", "how", "explain", "describe", "tell me"]):
            return {"intent": "question", "text": text}
        
        commands = ["weather", "news", "calculate", "convert", "password", "time", "date", "joke", "fact", "quote", "search", "wiki", "define", "crypto", "bitcoin", "ethereum", "translate", "dice", "coin", "random", "bmi", "tip", "age", "unit", "hash", "base64", "reverse", "uppercase", "lowercase", "word count", "ip", "system", "riddle", "would you rather", "note", "todo", "list", "rock paper", "guess", "emoji", "ascii", "color", "horoscope"]
        if any(t.startswith(c) or f" {c}" in t for c in commands):
            return {"intent": "command", "text": text}
        
        entertainment = ["joke", "funny", "laugh", "fact", "trivia", "quote", "inspiration", "sing", "poem", "story", "riddle", "would you"]
        if any(w in t for w in entertainment):
            return {"intent": "entertainment", "text": text}
        
        return {"intent": "chat", "text": text}


# ==================== MAIN AI ====================

class ProAI:
    def __init__(self):
        self.name = "Assistant"
        self.version = "11.0"
        self.config = Config()
        self.knowledge = KnowledgeBase()
        
        self.user_name = self.config.get_name()
        self.conv_count = 0
    
    def chat(self, user_input: str) -> str:
        self.conv_count += 1
        parsed = IntentParser.parse(user_input)
        intent = parsed["intent"]
        
        if intent == "question":
            return self._handle_question(user_input)
        elif intent == "command":
            return self._handle_command(user_input)
        elif intent == "entertainment":
            return self._handle_entertainment(user_input)
        else:
            return self._handle_chat(user_input)
    
    def _handle_question(self, text: str) -> str:
        t = text.lower()
        
        patterns = [
            r"what is (?:a |an |the )?(.+)",
            r"who is (?:the )?(.+)",
            r"what'?s (?:a |an |the )?(.+)",
            r"explain (.+)",
            r"describe (.+)",
            r"tell me about (.+)",
            r"define (.+)",
        ]
        
        topic = None
        for pattern in patterns:
            match = re.search(pattern, t)
            if match:
                topic = match.group(1).strip().rstrip("?")
                break
        
        if not topic:
            words = text.split()
            stop_words = {"what", "is", "are", "was", "were", "who", "how", "why", "where", "when", "the", "a", "an", "describe", "explain", "tell", "me", "about"}
            topic = " ".join([w for w in words if w.lower() not in stop_words and len(w) > 2])
        
        if topic:
            kb_result = self.knowledge.get(topic)
            if kb_result:
                return kb_result
            
            wiki = WebAPIs.get_wikipedia_summary(topic)
            if wiki.get("success"):
                return f"📖 {wiki['title']}\n\n{wiki['text'][:300]}...\n\n🔗 {wiki.get('url', '')}"
            
            if " " not in topic and len(topic) < 20:
                definition = WebAPIs.define_word(topic.split()[0])
                if definition.get("success"):
                    result = f"📖 {definition['word']}"
                    if definition.get("phonetic"):
                        result += f" {definition['phonetic']}"
                    result += "\n\n"
                    for d in definition.get("definitions", [])[:2]:
                        result += f"({d['part']}) {d['def']}\n"
                    return result
            
            search = WebAPIs.search_wikipedia(topic)
            if search.get("success"):
                result = f"🔍 Search results for '{topic}':\n\n"
                for r in search.get("results", [])[:3]:
                    result += f"• {r['title']}\n  {r['desc'][:80]}...\n\n"
                return result
        
        return f"I don't have a specific answer for that. Try rephrasing!"
    
    def _handle_command(self, text: str) -> str:
        t = text.lower()
        
        # Weather
        if t.startswith("weather ") or t == "weather":
            city = text.split(" ", 1)[1] if " " in text else "London"
            result = WebAPIs.get_weather(city, self.config.get_key("weather"))
            if result.get("success"):
                icon = "📡" if result.get("source") == "live" else "🎲"
                return f"{icon} Weather in {result['city']}\n\n🌡️ {result['temp']}°C (feels {result['feels']}°C)\n💧 {result['humidity']}%\n☁️ {result['desc'].title()}"
            return "Could not get weather"
        
        # News
        if t in ["news", "headlines", "latest news"]:
            result = WebAPIs.get_news(self.config.get_key("news"))
            if result.get("success"):
                return "📰 Latest News:\n\n" + "\n".join(f"• {a['title']}" for a in result.get("articles", [])[:5])
            return "Could not fetch news"
        
        # Calculator
        if t.startswith("calculate ") or t.startswith("calc ") or "what is " in t:
            expr = text.lower()
            for phrase in ["what is ", "calculate ", "calc "]:
                expr = expr.replace(phrase, "")
            expr = expr.rstrip("?")
            try:
                result = eval(expr, {"__builtins__": {}, "math": math, "sqrt": math.sqrt, "pi": math.pi, "e": math.e, "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log, "abs": abs, "round": round, "pow": pow, "max": max, "min": min})
                return f"🧮 {expr} = {result}"
            except:
                pass
        
        # Password
        if t.startswith("password") or "generate password" in t:
            length = int(re.findall(r"\d+", t)[0]) if re.findall(r"\d+", t) else 16
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
            pwd = ''.join(secrets.choice(chars) for _ in range(min(length, 64)))
            return f"🔐 Generated password ({len(pwd)} chars):\n{pwd}"
        
        # Time/Date
        if t == "time":
            return f"🕐 {datetime.now().strftime('%H:%M:%S')}"
        if t == "date":
            return f"📅 {datetime.now().strftime('%A, %B %d, %Y')}"
        if t == "datetime":
            return f"📅🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # UUID
        if t in ["uuid", "guid", "generate uuid"]:
            return f"🆔 {uuid.uuid4()}"
        
        # Define
        if t.startswith("define ") or "meaning of" in t:
            word = text.split(" ", 1)[1] if " " in text else text.replace("define ", "").replace("meaning of ", "")
            result = WebAPIs.define_word(word.split()[0])
            if result.get("success"):
                response = f"📖 {result['word']}"
                if result.get("phonetic"):
                    response += f" {result['phonetic']}"
                response += "\n\n"
                for d in result.get("definitions", [])[:2]:
                    response += f"({d['part']}) {d['def']}\n"
                return response
            return f"Could not find definition for '{word}'"
        
        # Currency
        if "convert" in t and any(c in t.upper() for c in ["USD", "EUR", "GBP", "JPY", "CNY", "INR", "CAD", "AUD"]):
            match = re.search(r"(\d+(?:\.\d+)?)\s*(\w+)\s+to\s+(\w+)", t)
            if match:
                amount, from_c, to_c = match.groups()
                result = CurrencyConverter.convert(float(amount), from_c, to_c)
                if result.get("success"):
                    return f"💱 {amount} {from_c.upper()} = {result['result']} {to_c.upper()}"
        
        # Crypto
        if any(c in t for c in ["crypto", "bitcoin", "btc", "ethereum", "eth", "solana", "dogecoin"]):
            coin = "BTC"
            if "eth" in t: coin = "ETH"
            elif "sol" in t: coin = "SOL"
            elif "dog" in t: coin = "DOGE"
            elif "xrp" in t: coin = "XRP"
            elif "ada" in t: coin = "ADA"
            elif "dot" in t: coin = "DOT"
            elif "matic" in t: coin = "MATIC"
            elif "ltc" in t: coin = "LTC"
            elif "bnb" in t: coin = "BNB"
            result = CryptoPrices.get_price(coin)
            if result.get("success"):
                arrow = "📈" if result["change"] > 0 else "📉"
                return f"₿ {coin}: ${result['price']:,} {arrow} {result['change']}%"
        
        # Dice
        if "dice" in t:
            sides = int(re.findall(r"\d+", t)[0]) if re.findall(r"\d+", t) else 6
            rolls = int(re.findall(r"(\d+)\s*dice", t)[0]) if re.findall(r"(\d+)\s*dice", t) else 1
            results = [random.randint(1, min(sides, 100)) for _ in range(min(rolls, 10))]
            return f"🎲 Rolled {rolls}d{sides}: {results}\nTotal: {sum(results)}"
        
        # Coin flip
        if "coin" in t and "flip" in t:
            result = random.choice(["Heads", "Tails"])
            return f"🪙 Coin flip: {result}!"
        
        # Random number
        if "random number" in t or "random" in t:
            match = re.search(r"(\d+)\s+to\s+(\d+)", t)
            if match:
                min_v, max_v = int(match.group(1)), int(match.group(2))
                return f"🎲 Random number ({min_v}-{max_v}): {random.randint(min_v, max_v)}"
            return f"🎲 Random number (1-100): {random.randint(1, 100)}"
        
        # BMI Calculator
        if "bmi" in t:
            match = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilos?)?" , t)
            match2 = re.search(r"(\d+(?:\.\d+)?)\s*(?:cm|meter|m)", t.replace("bmi", ""))
            if match or match2:
                return "📊 BMI Calculator: Tell me your weight in kg and height in cm\nExample: 'bmi 70kg 175cm'"
            return "📊 BMI Calculator: Say 'bmi [weight]kg [height]cm'\nExample: 'bmi 70kg 175cm'"
        
        # BMI actual calculation
        bmi_match = re.search(r"bmi\s+(\d+(?:\.\d+)?)\s*kg?\s+(\d+(?:\.\d+)?)\s*cm?", t)
        if bmi_match:
            weight = float(bmi_match.group(1))
            height = float(bmi_match.group(2)) / 100
            bmi = weight / (height * height)
            category = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
            return f"📊 BMI Results:\n\nWeight: {weight}kg\nHeight: {height*100}cm\nBMI: {bmi:.1f}\nCategory: {category}"
        
        # Tip calculator
        if "tip" in t:
            match = re.search(r"tip\s+(\d+(?:\.\d+)?)\s*(?:USD|EUR|GBP|\$|€|£)?\s*(?:at\s+)?(\d+)?%", t)
            if match:
                amount = float(match.group(1))
                percent = int(match.group(2)) if match.group(2) else 15
                tip = amount * percent / 100
                return f"💵 Tip Calculator:\n\nBill: ${amount:.2f}\nTip ({percent}%): ${tip:.2f}\nTotal: ${amount + tip:.2f}"
            return "💵 Tip Calculator: Say 'tip 50 at 20%'"
        
        # Age from birth year
        age_match = re.search(r"age\s+(?:of|from|born)?\s*(\d{4})", t)
        if age_match:
            birth_year = int(age_match.group(1))
            age = datetime.now().year - birth_year
            return f"🎂 Age: {age} years old"
        
        # Unit conversion
        if "convert" in t and any(u in t for u in ["km", "mile", "m", "cm", "kg", "lb", "celsius", "fahrenheit"]):
            match = re.search(r"(\d+(?:\.\d+)?)\s*(\w+)\s+to\s+(\w+)", t)
            if match:
                val, from_u, to_u = float(match.group(1)), match.group(2), match.group(3)
                result = UnitConverter.convert_length(val, from_u, to_u)
                if result:
                    return f"📐 {val} {from_u} = {result} {to_u}"
                result = UnitConverter.convert_weight(val, from_u, to_u)
                if result:
                    return f"⚖️ {val} {from_u} = {result} {to_u}"
                result = UnitConverter.convert_temp(val, from_u, to_u)
                if result:
                    return f"🌡️ {val}°{from_u.upper()} = {result}°{to_u.upper()}"
        
        # Text tools
        if "word count" in t:
            return "📝 Word Count: Say 'count [text]' or paste text after 'count'"
        
        if t.startswith("count "):
            text_to_count = text[6:]
            counts = TextTools.word_count(text_to_count)
            return f"📝 Word Count Results:\n\nWords: {counts['words']}\nCharacters: {counts['chars']}\nCharacters (no spaces): {counts['chars_no_spaces']}\nLines: {counts['lines']}"
        
        if "reverse" in t:
            text_to_reverse = text.split("reverse ", 1)[1] if "reverse " in t else ""
            if text_to_reverse:
                return f"🔄 Reversed:\n{TextTools.reverse_text(text_to_reverse)}"
        
        if "uppercase" in t:
            text_to_upper = text.split("uppercase ", 1)[1] if "uppercase " in t else text[10:]
            return f"🔠 {TextTools.uppercase(text_to_upper)}"
        
        if "lowercase" in t:
            text_to_lower = text.split("lowercase ", 1)[1] if "lowercase " in t else text[10:]
            return f"🔡 {TextTools.lowercase(text_to_lower)}"
        
        if "base64 encode" in t:
            text_to_encode = text.split("encode ", 1)[1] if "encode " in t else text[11:]
            return f"🔒 Base64 encoded:\n{TextTools.base64_encode(text_to_encode)}"
        
        if "base64 decode" in t or "decode base64" in t:
            text_to_decode = text.split("decode ", 1)[1] if "decode " in t else text[12:]
            return f"🔓 Decoded:\n{TextTools.base64_decode(text_to_decode)}"
        
        if "hash md5" in t or "md5 hash" in t:
            text_to_hash = text.split("hash ", 1)[1] if "hash " in t else text[8:]
            return f"🔑 MD5 Hash:\n{TextTools.hash_md5(text_to_hash)}"
        
        if "hash sha256" in t or "sha256 hash" in t:
            text_to_hash = text.split("hash ", 1)[1] if "hash " in t else text[11:]
            return f"🔑 SHA256 Hash:\n{TextTools.hash_sha256(text_to_hash)}"
        
        # IP Address
        if t in ["ip", "my ip", "ip address"]:
            ip_info = WebAPIs.get_ip_info()
            if ip_info.get("success"):
                d = ip_info["data"]
                return f"🌐 Your IP Info:\n\nIP: {d.get('ip', 'N/A')}\nCity: {d.get('city', 'N/A')}\nRegion: {d.get('region', 'N/A')}\nCountry: {d.get('country_name', 'N/A')}\nISP: {d.get('org', 'N/A')}"
            return "🌐 IP: Could not fetch IP info"
        
        # System info
        if t in ["system", "system info", "systeminfo"]:
            return f"💻 System Info:\n\nOS: {platform.system()}\nOS Version: {platform.version()}\nMachine: {platform.machine()}\nProcessor: {platform.processor()}\nPython: {platform.python_version()}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Notes
        if "note" in t and "add" in t:
            note = text.split("add note ", 1)[1] if "add note " in t else text.split("note ", 1)[1] if "note " in t else ""
            if note:
                self.config.add_note(note)
                return f"📝 Note added: {note}"
        
        if t in ["notes", "list notes", "show notes"]:
            notes = self.config.get_notes()
            if notes:
                result = "📝 Your Notes:\n\n"
                for i, n in enumerate(notes[-10:], 1):
                    result += f"{i}. {n['text']}\n   ({n['time'][:10]})\n"
                return result
            return "📝 No notes yet. Say 'add note [text]'"
        
        # Todos
        if "todo" in t and "add" in t:
            todo = text.split("add todo ", 1)[1] if "add todo " in t else ""
            if todo:
                self.config.add_todo(todo)
                return f"✅ Todo added: {todo}"
        
        if t in ["todos", "list todos", "show todos", "todo list"]:
            todos = self.config.get_todos()
            if todos:
                result = "📋 Your Todos:\n\n"
                for i, t in enumerate(todos[-10:], 1):
                    status = "✓" if t["done"] else "○"
                    result += f"{i}. [{status}] {t['text']}\n"
                result += "\nSay 'todo [number]' to toggle"
                return result
            return "📋 No todos yet. Say 'add todo [task]'"
        
        # Toggle todo
        todo_toggle = re.search(r"todo\s+(\d+)", t)
        if todo_toggle:
            idx = int(todo_toggle.group(1)) - 1
            self.config.toggle_todo(idx)
            todos = self.config.get_todos()
            if 0 <= idx < len(todos):
                status = "done" if todos[idx]["done"] else "not done"
                return f"✅ Todo {idx+1} marked as {status}"
        
        # Rock Paper Scissors
        if "rock paper" in t or "rps" in t:
            choices = ["Rock", "Paper", "Scissors"]
            user_choice = None
            if "rock" in t: user_choice = "Rock"
            elif "paper" in t: user_choice = "Paper"
            elif "scissor" in t: user_choice = "Scissors"
            
            if user_choice:
                ai_choice = random.choice(choices)
                result = f"🪨📄✂️ You: {user_choice} | AI: {ai_choice}\n\n"
                if user_choice == ai_choice:
                    result += "It's a tie!"
                elif (user_choice == "Rock" and ai_choice == "Scissors") or (user_choice == "Paper" and ai_choice == "Rock") or (user_choice == "Scissors" and ai_choice == "Paper"):
                    result += "You win! 🎉"
                else:
                    result += "AI wins!"
                return result
            return "🪨📄✂️ Rock Paper Scissors: Say 'rock', 'paper', or 'scissors'"
        
        # Number guessing game
        if "guess" in t and "number" in t:
            if not hasattr(self, 'guess_number'):
                self.guess_number = random.randint(1, 100)
                self.guess_attempts = 0
            return "🎯 Number Guessing Game: I'm thinking of a number 1-100. Say 'guess [number]'"
        
        guess_match = re.search(r"guess\s+(\d+)", t)
        if guess_match and hasattr(self, 'guess_number'):
            self.guess_attempts += 1
            user_num = int(guess_match.group(1))
            if user_num == self.guess_number:
                result = f"🎉 Correct! You guessed {self.guess_number} in {self.guess_attempts} attempts!"
                del self.guess_number
                del self.guess_attempts
                return result
            elif user_num < self.guess_number:
                return f"📈 Higher! (Attempt {self.guess_attempts})"
            else:
                return f"📉 Lower! (Attempt {self.guess_attempts})"
        
        # ASCII Art
        if "ascii" in t and "art" in t:
            arts = {
                "shrug": "¯\\_(ツ)_/¯",
                "tableflip": "(╯°□°)╯︵ ┻━┻",
                "unflip": "┬─┬ノ( º _ ºノ)",
                "lenny": "( ͡° ͜ʖ ͡°)",
                "disapproval": "ಠ_ಠ",
                "sunglasses": "(•_•) ( •_•)>⌐■-■ (⌐■_■)",
            }
            result = "🎨 ASCII Art:\n\n"
            for name, art in arts.items():
                result += f"{name}: {art}\n"
            return result
        
        # Emoji meanings
        if "emoji" in t and "meaning" in t:
            meanings = {
                "😊": "Smiling Face with Smiling Eyes - Joy, happiness",
                "😂": "Face with Tears of Joy - Laughing hard",
                "❤️": "Red Heart - Love, affection",
                "👍": "Thumbs Up - Like, approval",
                "🎉": "Party Popper - Celebration",
                "🔥": "Fire - Hot, trendy, lit",
                "💀": "Skull - Dead, funny",
                "🤔": "Thinking Face - Thinking",
                "😎": "Smiling Face with Sunglasses - Cool",
                "😭": "Loudly Crying Face - Very sad or happy",
            }
            result = "😀 Emoji Meanings:\n\n"
            for emo, mean in meanings.items():
                result += f"{emo} = {mean}\n"
            return result
        
        # API keys
        if "api key" in t or "set api" in t:
            return "🔑 To set API keys, edit config.json:\n\n• weather - OpenWeatherMap\n• news - NewsAPI\n\nOr ask me for help!"
        
        # Help
        if "help" in t or "commands" in t:
            return self._get_help()
        
        return f"I don't understand that. Try 'help' for all commands!"
    
    def _handle_entertainment(self, text: str) -> str:
        t = text.lower()
        
        if "joke" in t:
            return f"😂 {random.choice(Entertainment.JOKES)}"
        
        if "fact" in t or "did you know" in t:
            return f"💡 {random.choice(Entertainment.FACTS)}"
        
        if "quote" in t or "inspiration" in t:
            q = random.choice(Entertainment.QUOTES)
            return f"💭 \"{q[0]}\"\n   — {q[1]}"
        
        if "trivia" in t or "quiz" in t:
            q = random.choice(Entertainment.TRIVIA)
            return f"❓ {q[0]}\n💡 {q[1]}"
        
        if "riddle" in t:
            q = random.choice(Entertainment.RIDDLES)
            return f"🧩 Riddle:\n\n{q[0]}\n\nSay 'answer' to reveal!"
        
        if "answer" in t and hasattr(self, 'last_riddle'):
            return f"💡 Answer: {self.last_riddle}"
        
        if "would you rather" in t or "would you" in t:
            q = random.choice(Entertainment.WOULD_YOU_RATHER)
            return f"🤔 {q[0]}\n\n{q[1]}"
        
        return "I'm not sure what entertainment you're looking for!"
    
    def _handle_chat(self, text: str) -> str:
        t = text.lower()
        
        if "my name is" in t:
            match = re.search(r"my name is (.+)", t)
            if match:
                self.user_name = match.group(1).strip().capitalize()
                self.config.set_name(self.user_name)
                return f"Nice to meet you, {self.user_name}! I'll remember that."
        
        name_prefix = f"{self.user_name}, " if self.user_name else ""
        
        greetings = ["hello", "hi", "hey", "greetings", "what's up", "howdy"]
        if any(g in t for g in greetings):
            responses = [
                f"{name_prefix}Hello! How can I help you today?",
                f"{name_prefix}Hey there! What can I do for you?",
                f"{name_prefix}Hi! Nice to see you!",
            ]
            return random.choice(responses)
        
        if "how are you" in t:
            return f"{name_prefix}I'm doing great! Ready to help you with anything!"
        
        if "your name" in t:
            return f"I'm {self.name}, your AI assistant!"
        
        if "thank" in t:
            return random.choice(["You're welcome!", "Happy to help!", "No problem!", "Anytime!"])
        
        if t in ["bye", "goodbye", "see you", "later"]:
            return f"Goodbye{name_prefix}! Come back anytime! 👋"
        
        if "weather" in t:
            return "Say 'weather [city]' to get weather! Like 'weather London'"
        
        if t in ["help", "commands", "what can you do"]:
            return self._get_help()
        
        kb_result = self.knowledge.get(t)
        if kb_result:
            return kb_result
        
        responses = [
            f"{name_prefix}That's interesting! Tell me more or ask me a question!",
            f"{name_prefix}I'm not sure how to respond to that. Try asking me something!",
            f"{name_prefix}Got it! Need help with something specific?",
            f"{name_prefix}Hmm, let me think... Actually, just ask me anything!",
        ]
        return random.choice(responses)
    
    def _get_help(self) -> str:
        return """🤖 AI Assistant Pro v11 - Commands:

📝 QUESTIONS:
• What is [topic]?
• Who is [person]?
• Define [word]

🔧 UTILITIES:
• weather [city]
• news
• calculate [math]
• password [length]
• convert [num] [from] to [to]
• crypto [coin]
• dice [X]d[Y]
• coin flip
• random [X] to [Y]
• bmi [weight]kg [height]cm
• tip [amount] at [X]%
• age [birth year]
• uuid / time / date

📝 TEXT TOOLS:
• count [text]
• reverse [text]
• uppercase [text]
• lowercase [text]
• base64 encode [text]
• base64 decode [text]
• hash md5 [text]
• hash sha256 [text]

💻 SYSTEM:
• ip / my ip
• system info

📋 PRODUCTIVITY:
• add note [text]
• notes
• add todo [task]
• todos / todo list
• todo [number] (toggle)

🎮 GAMES:
• rock / paper / scissors
• guess [number]

🎨 FUN:
• joke / fact / quote
• trivia / riddle
• would you rather
• ascii art
• emoji meaning

💬 CHAT:
• Tell me your name!
• Ask me anything!

Just type naturally!"""


# ==================== GUI ====================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant Pro v11")
        self.root.geometry("1000x800")
        self.root.minsize(600, 500)
        
        self.colors = {
            "bg": "#0a0a0f",
            "bg2": "#12121a",
            "bg3": "#1a1a25",
            "text": "#e0e0e0",
            "text_dim": "#8888aa",
            "green": "#00d4aa",
            "blue": "#5ea8ff",
            "purple": "#a78bfa",
            "accent": "#00b894",
            "red": "#ff6b6b",
            "orange": "#ffa502",
        }
        
        self.root.configure(bg=self.colors["bg"])
        self.ai = ProAI()
        
        self._setup_ui()
        self._welcome()
    
    def _setup_ui(self):
        header = tk.Frame(self.root, bg=self.colors["bg"])
        header.pack(fill="x", padx=25, pady=(20, 15))
        
        tk.Label(header, text="◈", font=("Arial", 32), bg=self.colors["bg"], fg=self.colors["green"]).pack(side="left")
        
        title_frame = tk.Frame(header, bg=self.colors["bg"])
        title_frame.pack(side="left", padx=15, fill="x", expand=True)
        
        tk.Label(title_frame, text="AI Assistant Pro v11", font=("Segoe UI", 22, "bold"), bg=self.colors["bg"], fg=self.colors["green"]).pack(anchor="w")
        tk.Label(title_frame, text="MAX FEATURES • Like ChatGPT, Claude", font=("Segoe UI", 10), bg=self.colors["bg"], fg=self.colors["text_dim"]).pack(anchor="w")
        
        btn_frame = tk.Frame(header, bg=self.colors["bg"])
        btn_frame.pack(side="right")
        
        for text, cmd, color in [
            ("Clear", self._clear, self.colors["red"]),
            ("Help", self._help, self.colors["blue"])
        ]:
            tk.Button(btn_frame, text=text, command=cmd, bg=color, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=18, pady=8, cursor="hand2").pack(side="left", padx=4)
        
        self.chat = scrolledtext.ScrolledText(
            self.root, bg=self.colors["bg2"], fg=self.colors["text"],
            font=("Segoe UI", 12), relief="flat", wrap="word",
            padx=25, pady=20, highlightthickness=0
        )
        self.chat.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.chat.tag_config("user", foreground=self.colors["blue"], spacing1=12, font=("Segoe UI", 12, "bold"))
        self.chat.tag_config("ai", foreground=self.colors["green"], spacing1=12, font=("Segoe UI", 12))
        self.chat.tag_config("system", foreground=self.colors["text_dim"], font=("Segoe UI", 10, "italic"))
        
        input_frame = tk.Frame(self.root, bg=self.colors["bg"])
        input_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        self.entry = tk.Entry(
            input_frame, bg=self.colors["bg3"], fg=self.colors["text"],
            font=("Segoe UI", 13), relief="flat", insertbackground=self.colors["green"],
            bd=0
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=12, ipady=10)
        self.entry.bind("<Return>", self._send)
        
        send_btn = tk.Button(
            input_frame, text="Send →", command=self._send,
            bg=self.colors["accent"], fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", padx=25, pady=8, cursor="hand2"
        )
        send_btn.pack(side="right")
        
        self.status = tk.Label(
            self.root, text="Ready • Ask me anything!",
            bg=self.colors["bg3"], fg=self.colors["text_dim"],
            font=("Segoe UI", 9), anchor="w", padx=20, pady=8
        )
        self.status.pack(fill="x")
    
    def _welcome(self):
        self._add("AI", """👋 Welcome to AI Assistant Pro v11 - MAX EDITION!

I'm your ultimate AI companion with TONS of features!

💬 Just talk to me naturally:
• Ask questions
• Use commands
• Play games
• Get stuff done

🎯 NEW FEATURES:
• Text tools (reverse, uppercase, hash, base64)
• Unit converter (length, weight, temperature)
• Games (dice, rock paper scissors, guessing)
• Productivity (notes, todos)
• System info (IP, system details)
• BMI & tip calculators
• ASCII art & emoji meanings

🔧 Try Commands:
• "weather London"
• "news"
• "joke"
• "dice 2d20"
• "rock"
• "add todo finish project"
• "system info"
• "help"

And MUCH more! 🚀""", "ai")
    
    def _send(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        
        self.entry.delete(0, "end")
        self._add("You", text, "user")
        self.status.config(text="Thinking...")
        
        threading.Thread(target=self._respond, args=(text,), daemon=True).start()
    
    def _respond(self, text: str):
        response = self.ai.chat(text)
        self.root.after(0, lambda: self._add("AI", response, "ai"))
        self.root.after(0, lambda: self.status.config(text=f"Ready • {self.ai.conv_count} messages"))
    
    def _add(self, sender: str, message: str, tag: str):
        self.chat.config(state="normal")
        self.chat.insert("end", f"{sender}: {message}\n\n", tag)
        self.chat.see("end")
        self.chat.config(state="disabled")
    
    def _clear(self):
        self.chat.config(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.config(state="disabled")
        self._welcome()
    
    def _help(self):
        self._add("AI", self.ai._get_help(), "ai")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
