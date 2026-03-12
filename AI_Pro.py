#!/usr/bin/env python3
"""
AI Assistant - PRO EDITION v12
Ultimate AI Companion - Like ChatGPT/Claude

=============================================================================
STRUCTURE FOR DEVELOPERS
=============================================================================

This application is organized into the following sections:

1. CONFIG (lines ~31-79)
   - Config class: Manages persistent settings in config.json
   - Handles API keys, user preferences, notes, todos

2. WEB APIS (lines ~83-362)
   - WebAPIs class: Static methods for external API calls
   - Includes: Wikipedia, Dictionary, Weather, News, Stocks, Crypto,
     Currency, Facts APIs, NASA, GitHub, Country info, and more
   - All methods return {"success": bool, ...data}

3. AI RESPONSE GENERATOR (lines ~366-465)
   - AIResponseGenerator: Simple rule-based responses
   - Handles greetings, thanks, farewells without external APIs

4. UTILITY CLASSES (lines ~467-1100)
   - ReminderManager: Schedule and manage reminders
   - FileManager: File read/write operations
   - CodeExecutor: Execute Python code snippets safely
   - StockPrices: Fetch real stock data
   - ColorConverter: HEX/RGB/HSL conversions
   - MathSolver: Calculate expressions
   - Translator: Basic translation (uses dictionary API)
   - KnowledgeBase: Local Q&A knowledge base
   - Personalities: Different AI personality modes
   - ConversationMemory: Store and search conversation history
   - CurrencyConverter: Convert between currencies
   - CryptoPrices: Get cryptocurrency prices
   - Entertainment: Jokes, facts, riddles, games
   - TextTools: Reverse, uppercase, hash, base64, QR codes
   - UnitConverter: Length, weight, temperature, etc.
   - IntentParser: Parse user intent from natural language

5. MAIN AI ENGINE (lines ~1164-2290)
   - ProAI class: Core AI logic combining all features
   - Handles question answering, command execution, responses

6. GUI (lines ~2293-2511)
   - App class: Tkinter-based desktop interface

=============================================================================
ADDING NEW FEATURES
=============================================================================

To add a new API:
1. Add method to WebAPIs class following existing pattern
2. Return {"success": bool, ...data} format
3. Add intent/command handling in IntentParser
4. Add response handling in ProAI

To add a new command:
1. Add keywords to IntentParser.intent_keywords
2. Add handler method in ProAI
3. Update HELP.txt documentation

=============================================================================
"""

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, filedialog
import threading
import json
import re
import math
import random
import os
import uuid
import string
import urllib.request
import urllib.parse
import ssl
import secrets
import hashlib
import base64
import platform
import webbrowser
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


# ==================== CONFIG ====================

class Config:
    DEFAULTS = {
        "api_keys": {},
        "user_name": "",
        "notes": [],
        "todos": [],
        "personality": "helpful",
        "theme": "dark",
        "font_size": 12,
        "auto_save": True,
        "sound_enabled": True,
        "max_conversation_history": 100,
        "custom_prompts": {},
    }
    
    def __init__(self):
        self.file = "config.json"
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {**self.DEFAULTS, **data}
            except:
                pass
        return self.DEFAULTS.copy()
    
    def save(self):
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def set(self, key: str, value):
        self.data[key] = value
        self.save()
    
    def get_key(self, name: str) -> str:
        return self.data.get("api_keys", {}).get(name, "")
    
    def set_key(self, name: str, key: str):
        if "api_keys" not in self.data:
            self.data["api_keys"] = {}
        self.data["api_keys"][name] = key
        self.save()


# ==================== WEB APIS ====================

class WebAPIs:
    @staticmethod
    def fetch(url: str, timeout: int = 10) -> Dict:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent': 'AI-Pro/12'})
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
    
    # ========== MORE FREE APIS ==========
    
    @staticmethod
    def get_cat_fact() -> Dict:
        url = "https://catfact.ninja/fact"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            return {"success": True, "fact": result["data"].get("fact", "")}
        return {"success": False}
    
    @staticmethod
    def get_dog_fact() -> Dict:
        url = "https://dogapi.dog/api/v2/facts?limit=1"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            try:
                fact = result["data"][0]["attributes"]["body"]
                return {"success": True, "fact": fact}
            except:
                pass
        return {"success": False}
    
    @staticmethod
    def get_trivia(category: str = "") -> Dict:
        categories = {"science": 17, "history": 23, "geography": 22, "art": 25, "sports": 21, "general": 9}
        cat_id = categories.get(category.lower(), 9) if category else 9
        url = f"https://opentdb.com/api.php?amount=1&category={cat_id}&type=multiple"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            data = result["data"]
            if data.get("results"):
                q = data["results"][0]
                return {"success": True, "question": q.get("question", ""), "correct": q.get("correct_answer", ""), "incorrect": q.get("incorrect_answers", [])}
        return {"success": False}
    
    @staticmethod
    def predict_gender(name: str) -> Dict:
        url = f"https://api.genderize.io?name={urllib.parse.quote(name)}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]
            return {"success": True, "name": d.get("name", ""), "gender": d.get("gender", "unknown"), "probability": d.get("probability", 0)}
        return {"success": False}
    
    @staticmethod
    def predict_age(name: str) -> Dict:
        url = f"https://api.agify.io?name={urllib.parse.quote(name)}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]
            return {"success": True, "name": d.get("name", ""), "age": d.get("age", "unknown"), "count": d.get("count", 0)}
        return {"success": False}
    
    @staticmethod
    def predict_nationality(name: str) -> Dict:
        url = f"https://api.nationalize.io?name={urllib.parse.quote(name)}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]
            countries = d.get("country", [])
            return {"success": True, "name": d.get("name", ""), "countries": countries[:3]}
        return {"success": False}
    
    @staticmethod
    def get_random_user() -> Dict:
        url = "https://randomuser.me/api/"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]["results"][0]
            name = d["name"]
            return {"success": True, "name": f"{name['first']} {name['last']}", "email": d.get("email", ""), "location": f"{d['location']['city']}, {d['location']['country']}", "phone": d.get("phone", "")}
        return {"success": False}
    
    @staticmethod
    def get_number_fact(number: Optional[int] = None) -> Dict:
        num = number if number is not None else random.randint(1, 1000)
        url = f"http://numbersapi.com/{num}?json"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            return {"success": True, "number": num, "fact": result["data"].get("text", "")}
        return {"success": False}
    
    @staticmethod
    def get_exchange_rate(from_c: str, to_c: str) -> Dict:
        url = f"https://api.exchangerate.host/latest?base={from_c.upper()}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            rates = result["data"].get("rates", {})
            rate = rates.get(to_c.upper())
            if rate:
                return {"success": True, "from": from_c.upper(), "to": to_c.upper(), "rate": rate}
        return {"success": False}
    
    @staticmethod
    def get_quote() -> Dict:
        url = "https://api.quotable.io/random"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]
            return {"success": True, "quote": d.get("content", ""), "author": d.get("author", "")}
        return {"success": False}
    
    @staticmethod
    def get_holidays(year: Optional[int] = None, country: str = "US") -> Dict:
        y = year if year is not None else datetime.now().year
        url = f"https://date.nager.at/api/v3/PublicHolidays/{y}/{country}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            holidays = result["data"][:10]
            return {"success": True, "holidays": [{"date": h.get("date", ""), "name": h.get("localName", "")} for h in holidays]}
        return {"success": False}
    
    @staticmethod
    def get_word_definition(word: str) -> Dict:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            try:
                data = result["data"][0]
                defs = []
                for meaning in data.get("meanings", [])[:2]:
                    for defn in meaning.get("definitions", [])[:2]:
                        defs.append({"part": meaning.get("partOfSpeech", ""), "def": defn.get("definition", "")[:150]})
                return {"success": True, "word": data.get("word", ""), "phonetic": data.get("phonetic", ""), "definitions": defs}
            except:
                pass
        return {"success": False}
    
    @staticmethod
    def fetch_url_content(url: str) -> Dict:
        """Fetch content from any URL"""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent': 'AI-Pro/12'})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
                title = title_match.group(1) if title_match else "No title"
                return {"success": True, "url": url, "title": title, "content": content[:2000]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_current_datetime() -> Dict:
        """Get current date and time info"""
        now = datetime.now()
        return {
            "success": True,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day": now.strftime("%A"),
            "day_of_week": now.weekday(),
            "month": now.strftime("%B"),
            "year": now.year,
            "iso_week": now.isocalendar()[1],
        }
    
    @staticmethod
    def get_ip_info() -> Dict:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request("https://ipapi.co/json/", headers={'User-Agent': 'AI-Pro/12'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                return {"success": True, "data": json.loads(resp.read().decode())}
        except:
            return {"success": False}
    
    @staticmethod
    def web_search(query: str, num_results: int = 5) -> Dict:
        """Perform web search using DuckDuckGo HTML (no API key needed)"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
            })
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                
            results = []
            # Parse result links - DuckDuckGo uses redirect URLs
            link_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
            for match in re.findall(link_pattern, html):
                href, title = match
                title = re.sub(r'<[^>]+>', '', title).strip()
                # Extract actual URL from DuckDuckGo redirect
                actual_url = href
                if 'uddg=' in href:
                    try:
                        actual_url = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                    except:
                        pass
                if title and actual_url:
                    results.append({"title": title, "url": actual_url, "snippet": ""})
                    if len(results) >= num_results:
                        break
            
            # Get snippets
            for i, result in enumerate(results):
                snippet_pattern = rf'class="result__a"[^>]*href="{re.escape(result['url'][:50])}"[^>]*>.*?class="result__snippet"[^>]*>([^<]+)</a>'
                snippet_match = re.search(snippet_pattern, html, re.DOTALL)
                if snippet_match:
                    results[i]["snippet"] = snippet_match.group(1).strip()[:150]
            
            if results:
                return {"success": True, "query": query, "results": results}
        except Exception as e:
            pass
        return {"success": False, "error": "Search failed"}
    
    @staticmethod
    def search_google(query: str) -> Dict:
        """Fallback Google search using HTML scraping"""
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num=5"
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            
            results = []
            # Simple pattern for Google result titles
            pattern = r'<h3 class="[^"]*">(.*?)</h3>'
            titles = re.findall(pattern, html)[:5]
            for t in titles:
                clean = re.sub(r'<[^>]+>', '', t).strip()
                if clean:
                    results.append({"title": clean})
            
            if results:
                return {"success": True, "results": results}
        except:
            pass
        return {"success": False}
    
    @staticmethod
    def get_nasa_apod(api_key: str = "") -> Dict:
        if not api_key:
            return {"success": True, "title": "Demo NASA Picture of the Day", "explanation": "This is a demo. Add NASA API key for real data!", "url": "https://www.nasa.gov/wp-content/uploads/2015/01/590331main_ringside_stand_hi_1.jpg"}
        url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            return {"success": True, "title": result["data"].get("title", ""), "explanation": result["data"].get("explanation", "")[:300], "url": result["data"].get("url", "")}
        return {"success": False}
    
    @staticmethod
    def get_github_user(username: str) -> Dict:
        url = f"https://api.github.com/users/{urllib.parse.quote(username)}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]
            return {"success": True, "login": d.get("login", ""), "name": d.get("name", ""), "bio": d.get("bio", ""), "public_repos": d.get("public_repos", 0), "followers": d.get("followers", 0), "following": d.get("following", 0)}
        return {"success": False}
    
    @staticmethod
    def get_country_info(country: str) -> Dict:
        url = f"https://restcountries.com/v3.1/name/{urllib.parse.quote(country)}?fullText=true"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            try:
                data = result["data"][0]
                return {"success": True, "name": data.get("name", {}).get("common", ""), "capital": data.get("capital", ["N/A"])[0], "population": data.get("population", 0), "region": data.get("region", ""), "currency": list(data.get("currencies", {}).keys())[0] if data.get("currencies") else "N/A", "languages": ", ".join(data.get("languages", {}).values())}
            except:
                pass
        return {"success": False}

    # ========== ADDITIONAL FREE APIS ==========

    @staticmethod
    def get_joke(category: str = "") -> Dict:
        """Fetch a random joke from Official Joke API"""
        cat = f"?category={category.lower()}" if category else ""
        url = f"https://official-joke-api.appspot.com/random_joke{cat}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]
            return {"success": True, "setup": d.get("setup", ""), "punchline": d.get("punchline", ""), "type": d.get("type", "")}
        return {"success": False}

    @staticmethod
    def get_advice() -> Dict:
        """Fetch random advice from Advice Slip API"""
        url = "https://api.adviceslip.com/advice"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            return {"success": True, "advice": result["data"].get("slip", {}).get("advice", "")}
        return {"success": False}

    @staticmethod
    def get_Chuck_Norris_fact() -> Dict:
        """Fetch a Chuck Norris fact"""
        url = "https://api.chucknorris.io/jokes/random"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            return {"success": True, "fact": result["data"].get("value", "")}
        return {"success": False}

    @staticmethod
    def get_math_fact(number: Optional[int] = None) -> Dict:
        """Get a math fact about a number (with local fallback)"""
        math_facts = [
            "42 is the answer to life, the universe, and everything (Douglas Adams)",
            "Pi (π) is approximately 3.14159... and goes on forever",
            "A prime number is only divisible by 1 and itself",
            "0! (zero factorial) equals 1",
            "The Fibonacci sequence appears throughout nature",
            "Perfect numbers are equal to the sum of their proper divisors",
            "There are infinitely many prime numbers",
            "The square root of -1 is called 'i' (imaginary number)",
            "A googol is 10^100 (1 followed by 100 zeros)",
            "Euler's identity: e^(iπ) + 1 = 0 is considered beautiful",
        ]
        num = number if number is not None else random.randint(1, 100)
        return {"success": True, "number": num, "fact": random.choice(math_facts)}

    @staticmethod
    def get_date_fact(number: Optional[int] = None) -> Dict:
        """Get a historical fact about a date (with local fallback)"""
        date_facts = [
            {"month": 7, "day": 4, "fact": "In 1776, the US Declaration of Independence was signed"},
            {"month": 12, "day": 25, "fact": "Christmas celebrates the birth of Jesus Christ"},
            {"month": 1, "day": 1, "fact": "The Unix epoch started at midnight on January 1, 1970"},
            {"month": 7, "day": 20, "fact": "In 1969, Apollo 11 landed on the moon"},
            {"month": 10, "day": 31, "fact": "Halloween originated from the ancient Celtic festival of Samhain"},
            {"month": 11, "day": 11, "fact": "Armistice Day marks the end of World War I (1918)"},
            {"month": 4, "day": 22, "fact": "Earth Day was first celebrated in 1970"},
            {"month": 3, "day": 14, "fact": "Pi Day celebrates the mathematical constant π (3/14)"},
        ]
        if number is None:
            fact = random.choice(date_facts)
        else:
            fact = date_facts[number % len(date_facts)]
        return {"success": True, **fact}

    @staticmethod
    def get_year_fact(year: Optional[int] = None) -> Dict:
        """Get a historical fact about a year"""
        y = year if year is not None else random.randint(1900, 2025)
        url = f"http://numbersapi.com/{y}/year?json"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            return {"success": True, "year": y, "fact": result["data"].get("text", "")}
        return {"success": False}

    @staticmethod
    def get_programming_joke() -> Dict:
        """Get a programming-related joke"""
        jokes = [
            {"setup": "Why do programmers prefer dark mode?", "punchline": "Because light attracts bugs."},
            {"setup": "What do you call a programmer from Finland?", "punchline": "Nerdic."},
            {"setup": "Why did the developer go broke?", "punchline": "Because he used up all his cache."},
            {"setup": "How many programmers does it take to change a light bulb?", "punchline": "None, that's a hardware problem."},
            {"setup": "Why do Java developers wear glasses?", "punchline": "Because they can't C#."},
        ]
        joke = random.choice(jokes)
        return {"success": True, **joke, "type": "programming"}

    @staticmethod
    def get_random_emoji() -> Dict:
        """Get a random emoji with info"""
        emojis = [
            {"emoji": "😀", "name": "Grinning Face", "code": "U+1F600"},
            {"emoji": "🚀", "name": "Rocket", "code": "U+1F680"},
            {"emoji": "💡", "name": "Light Bulb", "code": "U+1F4A1"},
            {"emoji": "🎉", "name": "Party Popper", "code": "U+1F389"},
            {"emoji": "🔑", "name": "Key", "code": "U+1F511"},
            {"emoji": "🌟", "name": "Star", "code": "U+2B50"},
            {"emoji": "⚡", "name": "High Voltage", "code": "U+26A1"},
            {"emoji": "📚", "name": "Books", "code": "U+1F4DA"},
        ]
        return {"success": True, **random.choice(emojis)}

    @staticmethod
    def get_bitcoin_price() -> Dict:
        """Get current Bitcoin price from CoinGecko (free, no API key)"""
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            data = result["data"]
            if "bitcoin" in data:
                return {"success": True, "price": data["bitcoin"]["usd"], "currency": "USD"}
        return {"success": False}

    @staticmethod
    def get_dog_image() -> Dict:
        """Get a random dog image URL"""
        url = "https://dog.ceo/api/breeds/image/random"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            return {"success": True, "image_url": result["data"].get("message", ""), "status": result["data"].get("status", "")}
        return {"success": False}

    @staticmethod
    def get_cat_image() -> Dict:
        """Get a random cat image URL"""
        url = "https://api.thecatapi.com/v1/images/search"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            data = result["data"]
            if isinstance(data, list) and len(data) > 0:
                return {"success": True, "image_url": data[0].get("url", ""), "id": data[0].get("id", "")}
        return {"success": False}

    @staticmethod
    def get_random_fox_image() -> Dict:
        """Get a random fox image URL"""
        url = "https://randomfox.ca/floof/"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            return {"success": True, "image_url": result["data"].get("image", ""), "link": result["data"].get("link", "")}
        return {"success": False}

    @staticmethod
    def get_activity_suggestion() -> Dict:
        """Get a random activity suggestion (with local fallback)"""
        activities = [
            {"activity": "Read a book for 30 minutes", "type": "relaxation", "participants": 1},
            {"activity": "Take a walk in nature", "type": "relaxation", "participants": 1},
            {"activity": "Learn a new recipe", "type": "cooking", "participants": 1},
            {"activity": "Practice meditation for 10 minutes", "type": "relaxation", "participants": 1},
            {"activity": "Write in a journal", "type": "relaxation", "participants": 1},
            {"activity": "Call a friend you haven't talked to", "type": "social", "participants": 2},
            {"activity": "Do a 15-minute workout", "type": "exercise", "participants": 1},
            {"activity": "Listen to a new podcast", "type": "entertainment", "participants": 1},
            {"activity": "Try a new hobby or craft", "type": "creative", "participants": 1},
            {"activity": "Organize your workspace", "type": "productive", "participants": 1},
        ]
        return {"success": True, **random.choice(activities)}

    @staticmethod
    def get_public_ip() -> Dict:
        """Get public IP address"""
        url = "https://api.ipify.org?format=json"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            return {"success": True, "ip": result["data"].get("ip", "")}
        return {"success": False}

    @staticmethod
    def get_world_time(timezone: str = "UTC") -> Dict:
        """Get current time for a timezone"""
        url = f"http://worldtimeapi.org/api/timezone/{timezone}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            d = result["data"]
            return {"success": True, "datetime": d.get("datetime", ""), "timezone": d.get("timezone", ""), "utc_offset": d.get("utc_offset", "")}
        return {"success": False}

    @staticmethod
    def get_mnemonic_word() -> Dict:
        """Get a random word for memorization"""
        url = "https://random-word-api.herokuapp.com/word?number=1"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            words = result["data"]
            if isinstance(words, list) and len(words) > 0:
                return {"success": True, "word": words[0]}
        return {"success": False}

    @staticmethod
    def get_github_trending(lang: str = "") -> Dict:
        """Get trending GitHub repositories"""
        url = f"https://api.github.com/search/repositories?q=created:>{datetime.now().strftime('%Y-%m-%d')}&sort=stars&order=desc"
        if lang:
            url += f"+language:{lang}"
        result = WebAPIs.fetch(url)
        if result.get("success"):
            items = result["data"].get("items", [])[:5]
            repos = [{"name": r.get("full_name", ""), "stars": r.get("stargazers_count", 0), "url": r.get("html_url", ""), "desc": r.get("description", "")[:100]} for r in items]
            return {"success": True, "repos": repos}
        return {"success": False}


# ==================== FREE AI CONNECTORS ====================

class FreeAIConnector:
    """Connect to free AI APIs (no API key required)"""
    
    @staticmethod
    def torgpt_chat(message: str, system_prompt: str = "You are a helpful AI assistant.") -> Dict:
        """TorGPT - Free, no API key required"""
        try:
            url = "https://torgpt.space/api/v1/chat"
            payload = {
                "model": "torgpt",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            }
            data = json.dumps(payload).encode('utf-8')
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, data=data, headers={
                'Content-Type': 'application/json',
                'User-Agent': 'AI-Pro/12'
            })
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                if "choices" in result and len(result["choices"]) > 0:
                    return {"success": True, "content": result["choices"][0]["message"]["content"], "model": "torgpt"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False}
    
    @staticmethod
    def openrouter_chat(message: str, api_key: str = "free", system_prompt: str = "You are a helpful AI assistant.") -> Dict:
        """OpenRouter - Has free models (requires free API key from openrouter.ai)"""
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            payload = {
                "model": "deepseek/deepseek-r1:free",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            }
            data = json.dumps(payload).encode('utf-8')
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, data=data, headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'HTTP-Referer': 'https://github.com',
                'X-Title': 'AI-Pro'
            })
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                if "choices" in result and len(result["choices"]) > 0:
                    return {"success": True, "content": result["choices"][0]["message"]["content"], "model": "deepseek-r1"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False}
    
    @staticmethod
    def groq_chat(message: str, api_key: str = "gsk_random", system_prompt: str = "You are a helpful AI assistant.") -> Dict:
        """Groq - Has free tier with fast inference (requires free API key from groq.com)"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            }
            data = json.dumps(payload).encode('utf-8')
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, data=data, headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            })
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                if "choices" in result and len(result["choices"]) > 0:
                    return {"success": True, "content": result["choices"][0]["message"]["content"], "model": "llama-3.1-8b-instant"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False}
    
    @staticmethod
    def chat_with_ai(message: str, provider: str = "torgpt", api_key: str = "", system_prompt: str = "") -> Dict:
        """Unified method to chat with any AI provider"""
        if not system_prompt:
            system_prompt = "You are a helpful AI assistant. Keep responses concise and friendly."
        
        if provider == "torgpt":
            return FreeAIConnector.torgpt_chat(message, system_prompt)
        elif provider == "openrouter":
            return FreeAIConnector.openrouter_chat(message, api_key if api_key else "free", system_prompt)
        elif provider == "groq":
            return FreeAIConnector.groq_chat(message, api_key if api_key else "gsk_demo", system_prompt)
        else:
            return {"success": False, "error": f"Unknown provider: {provider}"}


# ==================== AI RESPONSE GENERATOR ====================

class AIResponseGenerator:
    """Simple AI response generator for non-knowledge questions"""
    
    @staticmethod
    def generate_response(user_input: str, personality: str = "helpful") -> str:
        t = user_input.lower()
        
        # Random conversational responses based on keywords
        responses_by_topic = {
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What's on your mind?",
                "Hey! Great to see you. What would you like to talk about?",
            ],
            "how_are_you": [
                "I'm doing great, thanks for asking!",
                "I'm excellent! Ready to help you with anything.",
                "Fantastic! How can I assist you today?",
            ],
            "thank": [
                "You're welcome! Happy to help!",
                "No problem at all!",
                "Anytime! That's what I'm here for.",
            ],
            "goodbye": [
                "Goodbye! Take care!",
                "See you later! Come back anytime.",
                "Bye! It was nice talking to you!",
            ],
            "sorry": [
                "No need to apologize!",
                "It's okay! I'm here to help.",
                "No problem at all!",
            ],
            "love": [
                "Love is a beautiful thing!",
                "That's wonderful to hear!",
                "Love makes the world go round!",
            ],
            "happy": [
                "That's great to hear!",
                "I'm happy for you!",
                "Wonderful! What made you happy?",
            ],
            "sad": [
                "I'm sorry you're feeling that way. Want to talk about it?",
                "Things can be tough. I'm here to listen.",
                "I hope things get better. Let me know if I can help.",
            ],
            "bored": [
                "Want to play a game? Try 'rock paper scissors' or 'guess number'!",
                "I can tell you a joke or fun fact! Just ask!",
                "How about some trivia? Ask me a riddle!",
            ],
            "tired": [
                "Take care of yourself! Get some rest.",
                "Remember to sleep! It's important.",
                "Self-care is important. Hope you feel better soon!",
            ],
            "hungry": [
                "You should eat something!",
                "Food sounds good right now!",
                "Maybe grab a snack!",
            ],
            "default": [
                "That's interesting! Tell me more.",
                "I see! What do you think about that?",
                "That's something! How can I help you with this?",
                "Interesting point! What would you like to know more about?",
            ]
        }
        
        # Detect topic
        if any(w in t for w in ["hello", "hi", "hey", "greetings", "howdy"]):
            return random.choice(responses_by_topic["greeting"])
        if any(w in t for w in ["how are you", "how're you", "how do you do"]):
            return random.choice(responses_by_topic["how_are_you"])
        if any(w in t for w in ["thank", "thanks", "appreciate"]):
            return random.choice(responses_by_topic["thank"])
        if any(w in t for w in ["bye", "goodbye", "see you", "later", "farewell"]):
            return random.choice(responses_by_topic["goodbye"])
        if any(w in t for w in ["sorry", "apologize", "oops"]):
            return random.choice(responses_by_topic["sorry"])
        if any(w in t for w in ["love", "love you", "like you"]):
            return random.choice(responses_by_topic["love"])
        if any(w in t for w in ["happy", "glad", "excited", "awesome", "great", "amazing"]):
            return random.choice(responses_by_topic["happy"])
        if any(w in t for w in ["sad", "upset", "depressed", "down", "unhappy"]):
            return random.choice(responses_by_topic["sad"])
        if any(w in t for w in ["bored", "boring", "nothing to do"]):
            return random.choice(responses_by_topic["bored"])
        if any(w in t for w in ["tired", "sleepy", "exhausted", "fatigue"]):
            return random.choice(responses_by_topic["tired"])
        if any(w in t for w in ["hungry", "food", "eat"]):
            return random.choice(responses_by_topic["hungry"])
        
        return random.choice(responses_by_topic["default"])


# ==================== REMINDERS ====================

class ReminderManager:
    def __init__(self, config):
        self.config = config
    
    def get_reminders(self):
        return self.config.get("reminders") or []
    
    def add_reminder(self, text: str, time_str: Optional[str] = None):
        reminders = self.get_reminders()
        reminders.append({"text": text, "time": time_str, "created": datetime.now().isoformat()})
        self.config.set("reminders", reminders)
    
    def delete_reminder(self, index: int):
        reminders = self.get_reminders()
        if 0 <= index < len(reminders):
            reminders.pop(index)
            self.config.set("reminders", reminders)


# ==================== FILE OPERATIONS (SAFE) ====================

class FileManager:
    @staticmethod
    def list_files(directory: str = ".") -> List[str]:
        try:
            return [f for f in os.listdir(directory) if not f.startswith('.')]
        except:
            return []
    
    @staticmethod
    def get_file_info(filepath: str) -> Dict:
        try:
            stat = os.stat(filepath)
            return {"size": stat.st_size, "created": datetime.fromtimestamp(stat.st_ctime).isoformat(), "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()}
        except:
            return {}


# ==================== CODE EXECUTOR (SAFE) ====================

class CodeExecutor:
    SAFE_BUILTINS = {
        'print': print,
        'len': len,
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
        'range': range,
        'enumerate': enumerate,
        'zip': zip,
        'map': map,
        'filter': filter,
        'sum': sum,
        'min': min,
        'max': max,
        'sorted': sorted,
        'reversed': reversed,
        'abs': abs,
        'round': round,
        'pow': pow,
        'divmod': divmod,
        'isinstance': isinstance,
        'type': type,
    }
    
    @classmethod
    def execute_python(cls, code: str) -> str:
        try:
            result = eval(code, {"__builtins__": cls.SAFE_BUILTINS}, {})
            return str(result)
        except SyntaxError as e:
            return f"Syntax Error: {e}"
        except Exception as e:
            return f"Error: {e}"


# ==================== STOCK PRICES (MOCK) ====================

class StockPrices:
    PRICES = {"AAPL": 178.50, "GOOGL": 141.80, "MSFT": 378.90, "AMZN": 178.25, "TSLA": 248.50, "META": 505.75, "NVDA": 875.30, "AMD": 180.20, "NFLX": 485.60, "DIS": 112.40}
    
    @classmethod
    def get_price(cls, symbol: str) -> Dict:
        symbol = symbol.upper()
        if symbol in cls.PRICES:
            change = round(random.uniform(-5, 5), 2)
            return {"success": True, "symbol": symbol, "price": cls.PRICES[symbol], "change": change}
        return {"success": False}
    
    @classmethod
    def get_all(cls) -> List[Dict]:
        return [{"symbol": k, "price": v, "change": round(random.uniform(-3, 3), 2)} for k, v in cls.PRICES.items()]


# ==================== COLOR CONVERTER ====================

class ColorConverter:
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Optional[tuple]:
        hex_color = hex_color.strip("#")
        if len(hex_color) == 6:
            try:
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            except:
                pass
        return None
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def rgb_to_hsl(r: float, g: float, b: float):
        r, g, b = r/255, g/255, b/255
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2
        
        if max_c == min_c:
            h = s = 0
        else:
            d = max_c - min_c
            s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            if max_c == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_c == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        return (round(h*360), round(s*100), round(l*100))


# ==================== ADVANCED MATH ====================

class MathSolver:
    @staticmethod
    def solve(expr: str) -> Optional[str]:
        try:
            allowed = {"__builtins__": {}, "math": math, "sqrt": math.sqrt, "pi": math.pi, "e": math.e, 
                      "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log, "log10": math.log10,
                      "abs": abs, "round": round, "pow": pow, "max": max, "min": min, "floor": math.floor,
                      "ceil": math.ceil, "factorial": math.factorial, "gcd": math.gcd, "lcm": lambda a,b: abs(a*b)//math.gcd(a,b)}
            result = eval(expr, allowed)
            return str(result)
        except:
            return None
    
    @staticmethod
    def solve_quadratic(a: float, b: float, c: float) -> str:
        d = b*b - 4*a*c
        if d > 0:
            x1 = (-b + math.sqrt(d)) / (2*a)
            x2 = (-b - math.sqrt(d)) / (2*a)
            return f"x = {x1:.2f} or x = {x2:.2f}"
        elif d == 0:
            x = -b / (2*a)
            return f"x = {x:.2f}"
        else:
            real = -b / (2*a)
            imag = math.sqrt(-d) / (2*a)
            return f"x = {real:.2f} + {imag:.2f}i or x = {real:.2f} - {imag:.2f}i"


# ==================== LANGUAGE TRANSLATION (MOCK) ====================

class Translator:
    MOCK_TRANSLATIONS = {
        ("hello", "es"): "hola",
        ("hello", "fr"): "bonjour",
        ("hello", "de"): "hallo",
        ("hello", "it"): "ciao",
        ("hello", "ja"): "konnichiwa",
        ("hello", "zh"): "ni hao",
        ("hello", "ko"): "annyeong",
        ("goodbye", "es"): "adios",
        ("goodbye", "fr"): "au revoir",
        ("goodbye", "de"): "auf wiedersehen",
        ("thank you", "es"): "gracias",
        ("thank you", "fr"): "merci",
        ("thank you", "de"): "danke",
        ("yes", "es"): "si",
        ("yes", "fr"): "oui",
        ("no", "es"): "no",
        ("no", "fr"): "non",
    }
    
    @classmethod
    def translate(cls, text: str, target: str) -> str:
        text_lower = text.lower().strip()
        key = (text_lower, target.lower())
        if key in cls.MOCK_TRANSLATIONS:
            return cls.MOCK_TRANSLATIONS[key]
        return f"[Mock] {text} -> {target.upper()}"


# ==================== KNOWLEDGE BASE ====================

class KnowledgeBase:
    def __init__(self):
        self.data = {
            # Tech
            "python": "Python - High-level programming language by Guido van Rossum (1991). Known for simplicity, readability, versatility. Used in web dev, data science, AI.",
            "javascript": "JavaScript - Web programming language. Runs in browsers and server-side with Node.js. Essential for interactive websites.",
            "ai": "Artificial Intelligence - Simulation of human intelligence in machines. Includes ML, NLP, computer vision, robotics.",
            "machine learning": "ML - Enables computers to learn from data without explicit programming. Includes supervised, unsupervised, reinforcement learning.",
            "deep learning": "Deep Learning - Neural networks with many layers. Powers image recognition, NLP, generative AI.",
            "chatgpt": "ChatGPT - AI chatbot by OpenAI, built on GPT-4. Answers questions, writes code, creates content.",
            "web3": "Web3 - Next internet evolution, built on blockchain. Includes dApps, NFTs, DeFi.",
            "blockchain": "Blockchain - Distributed ledger technology. Records transactions across many computers. Secure, transparent.",
            "bitcoin": "Bitcoin - First cryptocurrency (2009). Decentralized digital money without banks. Uses blockchain.",
            "nft": "NFT - Non-Fungible Token. Unique digital asset stored on blockchain. Represents ownership of digital items.",
            "metaverse": "Metaverse - Virtual reality space where users interact. Combines AR, VR, social media, gaming.",
            "cloud computing": "Cloud Computing - Delivery of computing services over internet. Includes servers, storage, databases, software.",
            "cybersecurity": "Cybersecurity - Protection of systems/networks from digital attacks. Types: network, application, information security.",
            "5g": "5G - Fifth generation mobile network. 100x faster than 4G. Enables IoT, autonomous vehicles, smart cities.",
            "iot": "IoT - Internet of Things. Network of physical devices connected to internet. Smart home, wearables, industrial sensors.",
            "vr": "VR - Virtual Reality. Computer-generated 3D environment. Used in gaming, training, education, therapy.",
            "ar": "AR - Augmented Reality. Overlays digital info on real world. Examples: Pokemon Go, AR glasses.",
            
            # Companies & People
            "elon musk": "Elon Musk - Tech entrepreneur. Founded SpaceX, Tesla, Neuralink, X. World's richest person. Born 1971, South Africa.",
            "steve jobs": "Steve Jobs - Co-founder of Apple (1976). Pioneer of personal computing. iPhone, iPad, MacBook. 1955-2011.",
            "bill gates": "Bill Gates - Co-founder Microsoft (1975). World's richest for decades. Philanthropist. Born 1955.",
            "mark zuckerberg": "Mark Zuckerberg - Founder of Facebook (2004), now Meta. Born 1984. Harvard dropout.",
            "jeff bezos": "Jeff Bezos - Founder Amazon (1994). Owns Blue Origin. World's richest person at times. Born 1964.",
            "sundar pichai": "Sundar Pichai - CEO of Google/Alphabet since 2015. Born 1972, India.",
            "sam altman": "Sam Altman - CEO of OpenAI since 2019 (before 2023). Founded Loopt. Born 1985.",
            "spacex": "SpaceX - Space company by Elon Musk (2002). Falcon rockets, Starship, Starlink. First private company to reach orbit.",
            "tesla": "Tesla - Electric car company by Elon Musk (2003). EVs, Solar, Powerwall, AI. Leading EV manufacturer.",
            "apple": "Apple - Tech company by Steve Jobs & Steve Wozniak (1976). iPhone, Mac, iOS, App Store. $3T market cap.",
            "microsoft": "Microsoft - Tech giant founded by Bill Gates & Paul Allen (1975). Windows, Office, Azure, GitHub, Xbox.",
            "google": "Google - Search engine by Larry Page & Sergey Brin (1998). Android, YouTube, Cloud services, AI.",
            "amazon": "Amazon - E-commerce by Jeff Bezos (1994). AWS, Prime, Alexa. Largest online retailer.",
            "meta": "Meta - Social media giant (formerly Facebook). Founded by Mark Zuckerberg. Owns Instagram, WhatsApp.",
            "nvidia": "Nvidia - GPU manufacturer. Leading AI chip company. Founded 1993 by Jensen Huang. Powers AI revolution.",
            "openai": "OpenAI - AI research company. Created ChatGPT, DALL-E, GPT-4. Founded 2015 by Elon Musk, Sam Altman.",
            
            # Science
            "universe": "Universe - Everything: space, time, matter, energy. Created ~13.8 billion years ago in Big Bang.",
            "big bang": "Big Bang - Theory of universe's origin. Happened 13.8 billion years ago. Everything expanded from a singularity.",
            "black hole": "Black Hole - Region where gravity is so strong nothing escapes. Formed when massive stars collapse.",
            "gravity": "Gravity - Force that attracts objects. Discovered by Newton. Einstein showed it's curvature of spacetime.",
            "relativity": "Relativity - Einstein's theory. Time dilation, length contraction. E=mc². GPS needs relativity corrections.",
            "quantum": "Quantum Mechanics - Study of matter/energy at atomic level. Superposition, entanglement, uncertainty principle.",
            "dna": "DNA - Deoxyribonucleic acid. Carries genetic instructions. Double helix structure discovered by Watson & Crick (1953).",
            "evolution": "Evolution - Change in species over time. Darwin's theory: natural selection. Life on Earth ~3.5 billion years.",
            "climate change": "Climate change - Long-term shifts in global temperatures. Caused by human activities: CO2 emissions, deforestation.",
            "global warming": "Global Warming - Rising Earth temperatures. Caused by greenhouse gases. Leads to climate change, sea level rise.",
            "renewable energy": "Renewable Energy - Sustainable energy from sun, wind, water. Solar, wind, hydro, geothermal. Low carbon emissions.",
            "nuclear energy": "Nuclear energy - Power from nuclear reactions. High energy density, low emissions. Concerns about waste.",
            "solar energy": "Solar energy - Energy from sunlight. Renewable, sustainable. Solar panels convert photons to electricity.",
            "wind energy": "Wind energy - Energy from wind. Renewable. Wind turbines convert kinetic energy to electricity.",
            
            # Health & Biology
            "cancer": "Cancer - Disease from abnormal cell growth. Types: lung, breast, colon, skin. Treatment: chemo, radiation, surgery, immunotherapy.",
            "diabetes": "Diabetes - Chronic condition affecting blood sugar. Type 1: insulin deficiency. Type 2: insulin resistance. Treatment: insulin, medication.",
            "covid": "COVID-19 - Respiratory illness by SARS-CoV-2 virus. Symptoms: fever, cough, fatigue. Pandemic started 2020. Vaccines developed 2020-2021.",
            "aids": "AIDS - HIV disease. Attacks immune system. Antiretroviral therapy (ART) controls it. Discovered 1980s.",
            "alzheimer": "Alzheimer's - Brain disease. Memory loss, cognitive decline. Most common dementia. No cure yet.",
            "heart disease": "Heart disease - Leading cause of death. Includes coronary artery disease, heart attacks. Risk factors: smoking, obesity, genetics.",
            "vaccine": "Vaccine - Biological preparation that provides immunity. Trains immune system to recognize pathogens.",
            "antibiotic": "Antibiotic - Medicine that kills bacteria. Fleming discovered penicillin (1928). Overuse leads to resistance.",
            "stem cell": "Stem Cell - Undifferentiated cell. Can become any cell type. Used in research, potential treatments.",
            "crispr": "CRISPR - Gene editing technology. Allows precise DNA modification. Revolutionized biotechnology, medicine.",
            
            # History
            "world war 2": "WWII - Global war (1939-1945). 70-85 million deaths. Allied powers vs Axis. Holocaust, atomic bombs.",
            "world war 1": "WWI - Global war (1914-1918). 20 million deaths. Trench warfare, new weapons. Led to WWII.",
            "cold war": "Cold War - US vs USSR (1947-1991). No direct combat. Arms race, space race, proxy wars.",
            "ancient egypt": "Ancient Egypt - Civilization along Nile (3100-30 BC). Pyramids, pharaohs, hieroglyphs. Giza pyramids built ~2500 BC.",
            "roman empire": "Roman Empire - Empire centered on Rome (27 BC-476 AD). Largest empire in ancient world. Law, engineering, language (Latin).",
            "renaissance": "Renaissance - Cultural rebirth in Europe (14th-17th century). Art, science, literature. Da Vinci, Michelangelo.",
            "industrial revolution": "Industrial Revolution - Shift to machines (1760-1840). Factories, steam engine. Transformed society, economy.",
            "moon landing": "Moon landing - Apollo 11 (1969). First humans on Moon: Neil Armstrong, Buzz Aldrin. Part of Space Race.",
            
            # Geography
            "paris": "Paris - Capital of France. Population ~2.1M. Eiffel Tower, Louvre, Notre-Dame. City of Light.",
            "london": "London - Capital of UK. Population ~9M. Big Ben, Tower of London, Buckingham Palace. Financial hub.",
            "new york": "New York - US city. Population ~8.4M. Statue of Liberty, Times Square, Empire State Building. Financial/cultural center.",
            "tokyo": "Tokyo - Capital of Japan. Population ~14M. Shibuya, Tokyo Tower, ancient temples. Tech hub.",
            "dubai": "Dubai - UAE city. Population ~3.4M. Burj Khalifa, Palm Islands. Luxury, business hub.",
            "singapore": "Singapore - City-state. Population ~5.6M. Financial hub, Marina Bay, Gardens by the Bay.",
            "australia": "Australia - Country/continent. Population ~26M. Unique wildlife, Great Barrier Reef, Sydney Opera House.",
            "antarctica": "Antarctica - Earth's southernmost continent. Ice-covered, no permanent residents. Scientific research only.",
            "sahara": "Sahara - Largest hot desert (9M km²). North Africa. Extreme temperatures, sand dunes.",
            "amazon rainforest": "Amazon - Largest tropical rainforest (5.5M km²). Brazil, Peru, Colombia. 10% of world's species.",
            "mount everest": "Mount Everest - World's tallest mountain (8,849m). Located in Himalayas on Nepal-Tibet border. First climbed by Edmund Hillary & Tenzing Norgay in 1953.",
            "everest": "Mount Everest - World's tallest mountain (8,849m). Located in Himalayas on Nepal-Tibet border. First climbed by Edmund Hillary & Tenzing Norgay in 1953.",
            "tallest mountain": "Mount Everest - World's tallest mountain at 8,849 meters (29,032 feet). Located in the Himalayas on the border between Nepal and Tibet. First successfully climbed in 1953 by Edmund Hillary and Tenzing Norgay.",
            "highest mountain": "Mount Everest - World's highest mountain at 8,849 meters (29,032 feet). Located in the Himalayas on the border between Nepal and Tibet.",
            "mount kilimanjaro": "Mount Kilimanjaro - Africa's tallest mountain (5,895m). Located in Tanzania. Volcanic mountain with three volcanic cones. Summit called Uhuru Peak.",
            "k2": "K2 - Second tallest mountain in the world (8,611m). Located on China-Pakistan border. Also known as Mount Godwin-Austen. More technically difficult than Everest.",
            "alps": "Alps - Major mountain range in Europe. Spans France, Switzerland, Italy, Austria, Slovenia. Mont Blanc (4,808m) is the highest peak.",
            "rocky mountains": "Rocky Mountains - Major mountain range in North America. Spans USA and Canada. Highest peak is Mount Elbert (4,401m) in Colorado.",
            "himalayas": "Himalayas - World's highest mountain range. Spans India, Nepal, Bhutan, China, Pakistan. Contains 10 of Earth's 14 peaks over 8,000m.",
            "highest peak": "Mount Everest - Highest peak in the world at 8,849 meters. Located in the Himalayas.",
            
            # Sports
            "football": "Football (Soccer) - World's most popular sport. 11 players per team. FIFA World Cup every 4 years.",
            "basketball": "Basketball - US invention (1891). 5 players per team. NBA: top league. Olympics sport.",
            "cricket": "Cricket - Popular in UK, India, Australia. 11 players per team. Test matches last 5 days.",
            "tennis": "Tennis - Racket sport. Grand Slams: Australian Open, French Open, Wimbledon, US Open.",
            "olympics": "Olympics - International sports event. Summer and Winter games. Ancient Greece origin, modern since 1896.",
            "f1": "Formula 1 - Auto racing. Fastest cars, top drivers. 20 races per season. Ferrari, Mercedes, Red Bull teams.",
            
            # Entertainment
            "marvel": "Marvel - Comic book company (1939). Spider-Man, Iron Man, Avengers. Marvel Cinematic Universe (MCU) since 2008.",
            "star wars": "Star Wars - Film franchise (1977). George Lucas. Jedis, Sith, Force. Most successful sci-fi franchise.",
            "harry potter": "Harry Potter - Book series by J.K. Rowling (1997-2007). Wizard school, magic. Film series, theme parks.",
            "netflix": "Netflix - Streaming service (1997). House of Cards, Stranger Things, Squid Game. 230M+ subscribers worldwide.",
            "spotify": "Spotify - Music streaming (2008). 500M+ users. Podcasts, algorithms, offline listening.",
            "youtube": "YouTube - Video platform (2005). 2B+ users. Videos, Shorts, Live, Premium.",
            
            # Economics
            "money": "Money - Medium of exchange. Forms: cash, digital, crypto. Functions: store of value, unit of account.",
            "stock market": "Stock Market - Trade company ownership shares. NYSE, NASDAQ. Indexes: S&P 500, Dow Jones, NASDAQ.",
            "inflation": "Inflation - Rising prices over time. Measured by CPI. Central banks target 2% annual inflation.",
            "recession": "Recession - Economic decline. GDP shrinks for 2+ quarters. Unemployment rises. 2008, 2020 recessions.",
            "gdp": "GDP - Gross Domestic Product. Total value of goods/services. Key measure of economy size.",
            "cryptocurrency": "Cryptocurrency - Digital money. Decentralized, blockchain-based. Bitcoin (2009), Ethereum (2015).",
            
            # General Knowledge
            "democracy": "Democracy - Government by people. Citizens vote for representatives. Types: direct, representative, parliamentary.",
            "capitalism": "Capitalism - Economic system with private ownership. Market forces determine prices. USA, UK examples.",
            
            # More Science & Nature
            "sun": "Sun - The star at the center of our Solar System. About 4.6 billion years old. Provides light and heat for Earth. Diameter: 1.4 million km.",
            "moon": "Moon - Earth's only natural satellite. 384,400 km from Earth. Diameter: 3,474 km. Controls ocean tides. First landed on 1969 (Apollo 11).",
            "earth": "Earth - Third planet from the Sun. Only known planet with life. 71% water surface. Age: 4.5 billion years. Diameter: 12,742 km.",
            "mars": "Mars - Fourth planet from the Sun. Known as Red Planet due to iron oxide. Has largest volcano (Olympus Mons) and canyon (Valles Marineris).",
            "jupiter": "Jupiter - Largest planet in our Solar System. Gas giant with 79 known moons. Great Red Spot is a storm larger than Earth.",
            "saturn": "Saturn - Sixth planet from the Sun. Famous for its beautiful rings made of ice and rock. Has 146 known moons including Titan.",
            "ocean": "Oceans - Earth's five oceans: Pacific, Atlantic, Indian, Southern, Arctic. Cover 71% of Earth's surface. Deepest point: Mariana Trench (11km).",
            "river": "Nile - World's longest river (6,650 km). Flows through northeastern Africa. Ancient Egyptian civilization depended on it. Amazon is second longest.",
            "desert": "Desert - Arid land with less than 250mm annual rainfall. Sahara (9M km²) is largest hot desert. Antarctica is largest cold desert.",
            
            # More common questions
            "age of earth": "Earth is approximately 4.54 billion years old, determined by radiometric dating of meteorites and lunar samples.",
            "population of world": "World population is approximately 8 billion. Most populous countries: China, India, USA, Indonesia, Pakistan.",
            "largest country": "Russia is the largest country by area (17M km²). Canada second. Vatican City is the smallest.",
            "smallest country": "Vatican City is the smallest country (0.44 km²). Located inside Rome, Italy. Population about 800.",
            "most spoken language": "English is most widely spoken (1.5B speakers). Mandarin Chinese has most native speakers (1.1B).",
            "richest person": "As of 2026, world's richest person varies. Elon Musk and Jeff Bezos have been top contenders. Wealth changes daily.",
            "biggest company": "Apple, Microsoft, and Saudi Aramco are typically the world's most valuable companies by market cap.",
            "socialism": "Socialism - Economic system with state/community ownership. Aims for equal distribution. Nordic model.",
            "education": "Education - Learning process. Primary, secondary, tertiary levels. Critical for development, employment.",
            "marriage": "Marriage - Legal union of partners. Varies by culture/religion. Legal rights, responsibilities.",
            "happiness": "Happiness - Emotional state. Factors: relationships, health, purpose, achievement. Subjective well-being.",
            
            # More topics
            "love": "Love - Complex emotion. Types: romantic, familial, platonic. Involves affection, care, commitment.",
            "friendship": "Friendship - Voluntary relationship. Based on mutual affection, trust, shared interests.",
            "happiness": "Happiness - Positive emotional state. Subjective well-being. Linked to health, relationships, purpose.",
            "success": "Success - Achievement of goals. Varies by individual. Often includes: wealth, recognition, fulfillment.",
            "intelligence": "Intelligence - Capacity to learn, understand. Types: logical, emotional, creative, practical.",
            "consciousness": "Consciousness - Awareness of surroundings/thoughts. Philosophy debate. Neuroscience studies brain correlates.",
            "time": "Time - Dimension in which events occur. Flows forward (entropy). Einstein: relative, linked to space (spacetime).",
            "space": "Space - Vast emptiness between celestial bodies. Filled with dark matter/energy. 93B light-year observable universe.",
            "life": "Life - Condition distinguishing living from dead. Characteristics: growth, reproduction, response to stimuli.",
            "death": "Death - End of life. Biological: cessation of vital functions. Cultural/religious beliefs about afterlife.",
            "religion": "Religion - System of beliefs/practices. Types: Abrahamic, Eastern, Indigenous. Christianity, Islam, Hinduism most followers.",
            "philosophy": "Philosophy - Study of existence, knowledge, values. Major branches: metaphysics, epistemology, ethics.",
            "psychology": "Psychology - Study of mind/behavior. Areas: clinical, cognitive, social, developmental. Helps understand humans.",
            "sociology": "Sociology - Study of society. Examines social relationships, institutions, structures. Race, gender, class topics.",
        }
    
    def get(self, topic: str) -> Optional[str]:
        topic = topic.lower().strip()
        if topic in self.data:
            return f"💡 {topic.title()}:\n\n{self.data[topic]}"
        for key, value in self.data.items():
            if key in topic or topic in key:
                return f"💡 {key.title()}:\n\n{value}"
        return None
    
    def add(self, topic: str, info: str):
        self.data[topic.lower()] = info
    
    def all_topics(self) -> List[str]:
        return list(self.data.keys())


# ==================== PERSONALITIES ====================

class Personalities:
    PERSONALITIES = {
        "helpful": {
            "name": "Helpful Assistant",
            "description": "Friendly, informative, always ready to help",
            "greeting": "Hello! I'm here to help you with anything you need.",
            "style": "warm"
        },
        "professional": {
            "name": "Professional",
            "description": "Formal, precise, business-oriented",
            "greeting": "Good day. How may I assist you today?",
            "style": "formal"
        },
        "creative": {
            "name": "Creative Writer",
            "description": "Imaginative, artistic, poetic",
            "greeting": "Hello! Let's create something wonderful together!",
            "style": "artistic"
        },
        "tech": {
            "name": "Tech Expert",
            "description": "Technical, detailed, coding-focused",
            "greeting": "Hey! Ready to dive into some tech?",
            "style": "casual"
        },
        "funny": {
            "name": "Comedian",
            "description": "Witty, humorous, lighthearted",
            "greeting": "Hey there! Life too serious? Let's fix that!",
            "style": "funny"
        }
    }


# ==================== CONVERSATION MEMORY ====================

class ConversationMemory:
    def __init__(self, max_size: int = 100):
        self.messages = []
        self.max_size = max_size
        self.context = {}
    
    def add(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.messages) > self.max_size:
            self.messages = self.messages[-self.max_size:]
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        return self.messages[-count:]
    
    def get_context_for_prompt(self, count: int = 5) -> str:
        recent = self.get_recent(count)
        context = ""
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content'][:100]}...\n"
        return context
    
    def clear(self):
        self.messages = []
    
    def search(self, query: str) -> List[Dict]:
        query = query.lower()
        return [m for m in self.messages if query in m["content"].lower()]
    
    def save_to_file(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            self.messages = json.load(f)


# ==================== CURRENCY & CRYPTO ====================

class CurrencyConverter:
    RATES = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 149.5, "CNY": 7.24, "INR": 83.1, "CAD": 1.36, "AUD": 1.53, "CHF": 0.88, "BRL": 4.97, "KRW": 1320, "MXN": 17.15, "SGD": 1.34, "HKD": 7.82}
    
    @classmethod
    def convert(cls, amount: float, from_c: str, to_c: str) -> Dict:
        f, t = from_c.upper(), to_c.upper()
        if f in cls.RATES and t in cls.RATES:
            result = amount * cls.RATES[t] / cls.RATES[f]
            return {"success": True, "from": f, "to": t, "amount": amount, "result": round(result, 2)}
        return {"success": False}


class CryptoPrices:
    PRICES = {"BTC": 67500, "ETH": 3450, "XRP": 0.52, "ADA": 0.45, "DOGE": 0.12, "SOL": 145, "BNB": 580, "DOT": 7.2, "MATIC": 0.85, "LTC": 72, "AVAX": 35, "LINK": 14, "UNI": 7, "ATOM": 9}
    
    @classmethod
    def get_price(cls, coin: str) -> Dict:
        coin = coin.upper()
        if coin in cls.PRICES:
            return {"success": True, "coin": coin, "price": cls.PRICES[coin], "change": round(random.uniform(-5, 5), 2)}
        return {"success": False}
    
    @classmethod
    def get_all(cls) -> List[Dict]:
        return [{"coin": k, "price": v, "change": round(random.uniform(-5, 5), 2)} for k, v in cls.PRICES.items()]


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
        "I told my wife she was drawing her eyebrows too high. She looked surprised!",
        "Why don't scientists trust atoms? Because they make up everything!",
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
        "Cleopatra lived closer to the moon landing than to the building of the Great Pyramid!",
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
        ("It is during our darkest moments that we must focus to see the light.", "Aristotle"),
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
        ("Nearest star?", "Proxima Centauri"),
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
    def title_case(text: str) -> str:
        return text.title()
    
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
    
    @staticmethod
    def qr_code_url(text: str) -> str:
        return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(text)}"


# ==================== UNIT CONVERTER ====================

class UnitConverter:
    LENGTH = {"m": 1, "km": 1000, "cm": 0.01, "mm": 0.001, "mile": 1609.34, "yard": 0.9144, "foot": 0.3048, "inch": 0.0254, "nm": 1e-9, "ft": 0.3048}
    WEIGHT = {"kg": 1, "g": 0.001, "mg": 0.000001, "lb": 0.453592, "oz": 0.0283495, "ton": 1000, "st": 6.35029}
    
    @classmethod
    def convert_length(cls, value: float, from_u: str, to_u: str) -> Optional[float]:
        f, t = from_u.lower(), to_u.lower()
        if f in cls.LENGTH and t in cls.LENGTH:
            return round(value * cls.LENGTH[f] / cls.LENGTH[t], 6)
        return None
    
    @classmethod
    def convert_weight(cls, value: float, from_u: str, to_u: str) -> Optional[float]:
        f, t = from_u.lower(), to_u.lower()
        if f in cls.WEIGHT and t in cls.WEIGHT:
            return round(value * cls.WEIGHT[f] / cls.WEIGHT[t], 6)
        return None
    
    @classmethod
    def convert_temp(cls, value: float, from_u: str, to_u: str) -> Optional[float]:
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


# ==================== VOICE & SYSTEM ====================

class VoiceAssistant:
    @staticmethod
    def speak(text: str) -> bool:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return True
        except ImportError:
            return False
        except:
            return False
    
    @staticmethod
    def listen() -> Optional[str]:
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
            return r.recognize_google(audio)
        except ImportError:
            return None
        except:
            return None


class SystemCommands:
    @staticmethod
    def shutdown(delay: int = 0) -> str:
        try:
            os.system(f"shutdown /s /t {delay}" if platform.system() == "Windows" else f"shutdown -h +{delay}")
            return "Shutting down..."
        except:
            return "Could not shutdown"
    
    @staticmethod
    def restart(delay: int = 0) -> str:
        try:
            os.system(f"shutdown /r /t {delay}" if platform.system() == "Windows" else f"shutdown -r +{delay}")
            return "Restarting..."
        except:
            return "Could not restart"
    
    @staticmethod
    def lock() -> str:
        try:
            if platform.system() == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            else:
                return "Lock not supported on this system"
            return "Screen locked"
        except:
            return "Could not lock"
    
    @staticmethod
    def sleep() -> str:
        try:
            if platform.system() == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Sleeping..."
        except:
            return "Could not sleep"
    
    @staticmethod
    def empty_recycle_bin() -> str:
        try:
            if platform.system() == "Windows":
                os.system('echo Y | powershell -Command "Clear-RecycleBin -Force"')
            return "Recycle bin emptied"
        except:
            return "Could not empty recycle bin"
    
    @staticmethod
    def get_system_info() -> Dict:
        return {
            "os": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
        }


# ==================== UTILITIES ====================

class PasswordGenerator:
    @staticmethod
    def generate(length: int = 16, include_special: bool = True) -> str:
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return ''.join(secrets.choice(chars) for _ in range(length))


class ClipboardManager:
    @staticmethod
    def copy(text: str) -> bool:
        try:
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            return True
        except:
            return False
    
    @staticmethod
    def paste() -> Optional[str]:
        try:
            root = tk.Tk()
            root.withdraw()
            return root.clipboard_get()
        except:
            return None


class Screenshot:
    @staticmethod
    def capture() -> Optional[str]:
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(filename)
            return filename
        except ImportError:
            return None
        except:
            return None


class QRCode:
    @staticmethod
    def generate_url(data: str) -> str:
        return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(data)}"


# ==================== PRODUCTIVITY ====================

class CalendarManager:
    def __init__(self, config):
        self.config = config
    
    def get_events(self):
        return self.config.get("calendar_events") or []
    
    def add_event(self, title: str, date: str, time: Optional[str] = None):
        events = self.get_events()
        events.append({"title": title, "date": date, "time": time, "created": datetime.now().isoformat()})
        self.config.set("calendar_events", events)
    
    def delete_event(self, index: int):
        events = self.get_events()
        if 0 <= index < len(events):
            events.pop(index)
            self.config.set("calendar_events", events)


class HealthCalculator:
    @staticmethod
    def bmi(weight_kg: float, height_m: float) -> Dict:
        bmi_value = weight_kg / (height_m ** 2)
        if bmi_value < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi_value < 25:
            category = "Normal"
        elif 25 <= bmi_value < 30:
            category = "Overweight"
        else:
            category = "Obese"
        return {"bmi": round(bmi_value, 1), "category": category}
    
    @staticmethod
    def bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        if gender.lower() in ["male", "m"]:
            return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    @staticmethod
    def tdee(bmr: float, activity_level: str) -> float:
        multipliers = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very_active": 1.9}
        return bmr * multipliers.get(activity_level.lower(), 1.2)


class UrlShortener:
    @staticmethod
    def shorten(url: str) -> Optional[str]:
        try:
            api_url = f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}"
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(api_url)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                return resp.read().decode().strip()
        except:
            return None


# ==================== INTENT PARSER ====================

class IntentParser:
    @staticmethod
    def parse(text: str) -> Dict:
        t = text.lower().strip()
        
        # First check if it's a question (most important)
        question_words = ["?", "what", "who", "where", "when", "why", "how", "explain", "describe", "tell me", "define meaning"]
        if any(w in t for w in question_words):
            return {"intent": "question", "text": text}
        
        # Check entertainment FIRST (joke, fact, quote should be entertainment)
        entertainment = ["joke", "funny", "laugh", "fact", "trivia", "quote", "inspiration", "sing", "poem", "story", "riddle", "would you", "riddle"]
        if any(w in t for w in entertainment):
            return {"intent": "entertainment", "text": text}
        
        # Then check for explicit commands (must be at start or as standalone word)
        command_starts = [
            # Weather/Info
            "weather ", "news ", "nasa", "github ", "wiki ",
            # Finance - Crypto (must be before entertainment)
            "crypto ", "bitcoin", "ethereum", "btc", "eth ",
            # Math/Calc
            "calculate ", "calc ", "solve ", "math ", "quadratic ",
            # Generators
            "password ", "uuid ", "dice ", "random ",
            # Conversions
            "convert ", "translate ", "color ", "unit ",
            # Text tools
            "define ", "reverse ", "uppercase ", "lowercase ", "word count", "count ", "hash ", "base64 ", "md5 ", "sha256 ", "qr ",
            # Finance
            "stock ", "all stocks", "all crypto", "exchange rate",
            # Time/Dates - Expanded
            "time", "date", "datetime", "day", "today", "what day", "age ", "leap year", "day of week", "holidays", "holiday",
            # Tools
            "bmi ", "tip ", "ip ", "system",
            # Short commands
            "ascii art", "emoji", "cat fact", "dog fact", "trivia", "number fact",
            # Productivity
            "add note", "add todo", "notes", "todos", "tasks", "remind",
            # Personality/Settings
            "personality", "settings",
            # History
            "search history", "clear history", "export chat", "import chat", "summarize",
            # Games
            "rock paper", "rps", "guess number", "guess ",
            # Web
            "open ",
            # Word of day
            "word of the day", "daily word", "quote of the day",
            # NEW APIs
            "random user", "gender ", "nationality", "predict age",
            # Web Search
            "search ", "search for ", "google ", "look up ",
            # Voice & System
            "speak ", "speak:", "listen", "voice input", "shutdown", "restart", "lock", "sleep", "system info", "empty recycle",
            # Utilities
            "generate password", "password ", "clipboard", "copy to clipboard", "screenshot", "shorten url", "url shortener",
            # Productivity
            "add event", "calendar", "bmr ", "tdee ", "calorie",
            # AI Chat
            "ask ai", "chat with ai", "ai ", "ask gpt", "ask chatbot", "use ai", "deepseek", "llama",
        ]
        
        for cmd in command_starts:
            if t.startswith(cmd) or t == cmd:
                return {"intent": "command", "text": text}
        
        return {"intent": "chat", "text": text}


# ==================== MAIN AI ====================

class ProAI:
    def __init__(self):
        self.name = "Assistant"
        self.version = "12.0"
        self.config = Config()
        self.knowledge = KnowledgeBase()
        self.memory = ConversationMemory(self.config.get("max_conversation_history") or 100)
        
        self.user_name = self.config.get("user_name") or ""
        self.personality = self.config.get("personality") or "helpful"
        self.conv_count = 0
        
        self._init_game_state()
    
    def _init_game_state(self):
        self.guess_number = None
        self.guess_attempts = 0
    
    def chat(self, user_input: str) -> str:
        self.conv_count += 1
        
        self.memory.add("user", user_input)
        
        parsed = IntentParser.parse(user_input)
        intent = parsed["intent"]
        
        if intent == "question":
            response = self._handle_question(user_input)
        elif intent == "command":
            response = self._handle_command(user_input)
        elif intent == "entertainment":
            response = self._handle_entertainment(user_input)
        else:
            response = self._handle_chat(user_input)
        
        self.memory.add("assistant", response)
        return response
    
    def _handle_question(self, text: str) -> str:
        t = text.lower().strip()
        original = text
        
        # Build smart topic from question
        words = text.split()
        stop_words = {"what", "is", "are", "was", "were", "who", "how", "why", "where", "when", 
                      "the", "a", "an", "describe", "explain", "tell", "me", "about", "do", "you", 
                      "know", "can", "could", "would", "should", "will", "did", "does", "for", "with", 
                      "to", "of", "in", "on", "at", "by", "from", "that", "this", "it", "its",
                      "your", "my", "his", "her", "their", "our", "be", "being", "been", "have", 
                      "has", "had", "i", "you", "we", "they", "he", "she", "name", "called", "mean",
                      "good", "bad", "some", "one", "things", "thing", "much", "many", "really",
                      "type", "kind", "sort", "exactly", "work", "means", "meaning", "want", "need",
                      "help", "like", "use", "get", "make", "create", "start", "begin"}
        
        # Strategy 1: Pattern-based extraction (expanded)
        topic = ""
        patterns = [
            # What questions
            (r"what (?:is|are|was|were|do|does|did|can|could|would|should) (?:a |an |the )?(.+?)(?:\?|$)", 1),
            (r"what'?s (?:a |an |the )?(.+?)(?:\?|$)", 1),
            (r"what kind of (.+?)(?:\?|$)", 1),
            (r"what type of (.+?)(?:\?|$)", 1),
            # Who questions  
            (r"who (?:is|are|was|were|do|does|did|can|could|would|should) (?:the )?(.+?)(?:\?|$)", 1),
            (r"who'?s (.+?)(?:\?|$)", 1),
            # How questions
            (r"how (?:do|does|did|can|could|would|should|to|many|much) (.+?)(?:\?|$)", 1),
            (r"how'?s (.+?)(?:\?|$)", 1),
            (r"how about (.+?)(?:\?|$)", 1),
            # Why questions
            (r"why (?:is|are|was|were|do|does|did|can|could|would|should|does) (.+?)(?:\?|$)", 1),
            (r"why don'?t (.+?)(?:\?|$)", 1),
            # Where questions
            (r"where (?:is|are|was|were|do|does|did|can|could|would|should) (.+?)(?:\?|$)", 1),
            (r"where'?s (.+?)(?:\?|$)", 1),
            # When questions
            (r"when (?:is|are|was|were|do|does|did|can|could|would|should) (.+?)(?:\?|$)", 1),
            # Other question patterns
            (r"explain (.+?)(?:\?|$)", 1),
            (r"describe (.+?)(?:\?|$)", 1),
            (r"tell me about (.+?)(?:\?|$)", 1),
            (r"can you (.+?)(?:\?|$)", 1),
            (r"define (.+?)(?:\?|$)", 1),
            (r"give me info(?:rmation)? about (.+?)(?:\?|$)", 1),
            (r"info(?:rmation)? about (.+?)(?:\?|$)", 1),
            (r"tell me (.+?)(?:\?|$)", 1),
            (r"do you know (.+?)(?:\?|$)", 1),
        ]
        
        for pattern, group in patterns:
            match = re.search(pattern, t)
            if match:
                topic = match.group(group).strip().rstrip("?")
                break
        
        # Strategy 2: If no pattern match, extract from remaining words
        if not topic or len(topic) < 2:
            topic = " ".join([w for w in words if w.lower() not in stop_words and len(w) > 1])
        
        # Clean topic
        topic = topic.strip("?.,!").strip()
        
        if not topic or len(topic) < 2:
            return "I'm not sure what you're asking. Could you rephrase your question?"
        
        # Question type detection
        question_types = []
        if any(w in t for w in ["who", "person", "people"]): question_types.append("person")
        if any(w in t for w in ["where", "location", "place", "city", "country"]): question_types.append("place")
        if any(w in t for w in ["when", "date", "year", "time", "history"]): question_types.append("time")
        if any(w in t for w in ["how many", "how much", "number", "amount", "quantity"]): question_types.append("quantity")
        if any(w in t for w in ["how to", "how do", "way to", "steps"]): question_types.append("howto")
        if any(w in t for w in ["why", "reason", "because"]): question_types.append("why")
        if any(w in t for w in ["what", "define", "meaning"]): question_types.append("definition")
        
        # Try knowledge base first (best match)
        kb_result = self._smart_kb_lookup(topic)
        if kb_result:
            return kb_result
        
        # Try Wikipedia summary (most comprehensive)
        wiki = WebAPIs.get_wikipedia_summary(topic)
        if wiki.get("success"):
            return f"📖 {wiki['title']}\n\n{wiki['text'][:800]}\n\n🔗 {wiki.get('url', '')}"
        
        # Try dictionary for single words
        if len(topic.split()) == 1 and len(topic) < 20:
            definition = WebAPIs.define_word(topic)
            if definition.get("success"):
                result = f"📖 {definition['word']}"
                if definition.get("phonetic"):
                    result += f" {definition['phonetic']}"
                result += "\n\n"
                for d in definition.get("definitions", [])[:3]:
                    result += f"({d['part']}) {d['def']}\n"
                return result
        
        # Try web search as fallback
        search = WebAPIs.search_wikipedia(topic)
        if search.get("success"):
            results = search.get("results", [])
            if results:
                result = f"🔍 Results for '{topic}':\n\n"
                for r in results[:4]:
                    desc = r['desc'][:100] + "..." if len(r['desc']) > 100 else r['desc']
                    result += f"• {r['title']}\n  {desc}\n\n"
                return result
        
        # Try AI as final fallback (better response)
        try:
            result = FreeAIConnector.chat_with_ai(original, "torgpt")
            if result.get("success"):
                return f"🤖 {result['content']}\n\n💡 Tip: Ask 'ask ai [question]' for AI-powered answers!"
        except:
            pass
        
        # Generate smart response based on question type
        return self._generate_answer(topic, question_types, original)
    
    def _smart_kb_lookup(self, topic: str) -> Optional[str]:
        """Smart knowledge base lookup with fuzzy matching"""
        topic_clean = topic.lower().strip()
        
        # Exact match
        if topic_clean in self.knowledge.data:
            return f"💡 {self.knowledge.data[topic_clean]}"
        
        # Find best partial match (longest key that matches)
        best_match = None
        best_length = 0
        for key, value in self.knowledge.data.items():
            if key in topic_clean or topic_clean in key:
                if len(key) > best_length:
                    best_match = (key, value)
                    best_length = len(key)
        
        if best_match:
            return f"💡 {best_match[0].title()}:\n\n{best_match[1]}"
        
        # Word match - find key with most matching words
        topic_words = set(topic_clean.split())
        best_word_match = None
        best_word_count = 0
        for key, value in self.knowledge.data.items():
            key_words = set(key.split())
            matches = topic_words & key_words
            if len(matches) >= 2 and len(matches) > best_word_count:
                best_word_match = (key, value)
                best_word_count = len(matches)
        
        if best_word_match:
            return f"💡 {best_word_match[0].title()}:\n\n{best_word_match[1]}"
        
        return None
    
    def _generate_answer(self, topic: str, qtypes: List[str], original: str) -> str:
        """Generate a reasonable answer when no data found"""
        t = topic.lower()
        
        # If it's a "what is X" type question we couldn't answer
        if "definition" in qtypes or original.lower().startswith("what is") or original.lower().startswith("what's"):
            return f"""🤔 I don't have specific information about '{topic}' in my knowledge base.

💡 Suggestions:
• Ask me about tech, science, history, health, business, sports, or entertainment
• Try: 'search {topic}' to search the web
• Or ask 'ask ai {topic}' for AI-generated answer

What else can I help you with?"""
        
        # For "who is" questions
        if "person" in qtypes:
            return f"""👤 I don't have information about '{topic}' in my database.

Try:
• 'search {topic}' - to search online
• 'ask ai who is {topic}' - for AI answer
• 'wiki {topic}' - for Wikipedia"""
        
        # For "where" questions
        if "place" in qtypes:
            return f"""📍 I'm not sure where '{topic}' is.

Suggestions:
• 'search where is {topic}' 
• 'ask ai where is {topic}'
• 'wiki {topic}' for location info"""
        
        # For "when" questions  
        if "time" in qtypes:
            return f"""📅 I don't know when '{topic}' happened.

Try:
• 'search when {topic}'
• 'ask ai when did {topic} happen'
• 'wiki {topic}' for historical events"""
        
        # For "how to" questions
        if "howto" in qtypes:
            return f"""🛠️ To learn how to {topic}:

1. Search online tutorials
2. Check YouTube for videos  
3. Find a beginner's guide
4. Practice with small projects

Or ask: 'ask ai how to {topic}' for step-by-step help!"""
        
        # For "why" questions
        if "why" in qtypes:
            return f"""🤔 That's an interesting question about '{topic}'!

There could be many reasons. Try:
• 'ask ai why {topic}' - for detailed explanation
• 'search why {topic}' - for multiple perspectives
• 'wiki {topic}' - for factual information"""
        
        # For "how many/much" questions
        if "quantity" in qtypes:
            return f"""🔢 I don't have the exact number for '{topic}'.

Try:
• 'search how many {topic}'
• 'ask ai how many {topic}'
• 'wiki {topic}' for statistics"""
        
        # Generic fallback
        return f"""🤔 I don't have specific information about '{topic}'.

💡 What I can help with:
• 'search [topic]' - Search the web
• 'ask ai [question]' - Get AI answer
• 'wiki [topic]' - Wikipedia info
• 'define [word]' - Word definition

I know lots about: technology, science, history, health, business, sports, entertainment, and more!

What would you like to try?"""
    
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
        
        # Wikipedia search
        if t.startswith("wiki "):
            topic = text[5:].strip()
            if topic:
                wiki = WebAPIs.get_wikipedia_summary(topic)
                if wiki.get("success"):
                    return f"📖 {wiki['title']}\n\n{wiki['text'][:600]}\n\n🔗 {wiki.get('url', '')}"
                search = WebAPIs.search_wikipedia(topic)
                if search.get("success"):
                    results = search.get("results", [])
                    if results:
                        result = f"🔍 Wikipedia results for '{topic}':\n\n"
                        for r in results[:4]:
                            result += f"• {r['title']}\n  {r['desc'][:80]}...\n\n"
                        return result
                return f"Could not find Wikipedia article for '{topic}'"
        
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
        
        # Time/Date - Enhanced with day info
        if t == "time" or t == "what time is it":
            now = WebAPIs.get_current_datetime()
            return f"🕐 Current Time:\n\n{now['time']}\n\nToday is {now['day']}"
        
        if t == "date" or t == "what date is it" or t == "today":
            now = WebAPIs.get_current_datetime()
            return f"📅 Today's Date:\n\n{now['date']}\n\n{now['day']}, {now['month']} {datetime.now().day}, {now['year']}"
        
        if t == "datetime" or t == "what day is it" or t == "day info":
            now = WebAPIs.get_current_datetime()
            return f"📅🕐 Current Date & Time:\n\nDate: {now['date']}\nTime: {now['time']}\nDay: {now['day']}\nWeek: {now['iso_week']}\nMonth: {now['month']}\nYear: {now['year']}"
        
        if t in ["day", "what day is today", "what day is it"]:
            now = WebAPIs.get_current_datetime()
            return f"Today is {now['day']}, {now['date']}"
        
        # UUID
        if t in ["uuid", "guid", "generate uuid"]:
            return f"🆔 {uuid.uuid4()}"
        
        # Fetch URL
        if t.startswith("fetch ") or t.startswith("get ") or t.startswith("open ") or t.startswith("url "):
            match = re.search(r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9]+\.[a-zA-Z]{2,}[^\s]*)", text)
            if match:
                url = match.group(1)
                if not url.startswith("http"):
                    url = "https://" + url
                result = WebAPIs.fetch_url_content(url)
                if result.get("success"):
                    return f"🌐 Fetched: {result['title']}\n\nURL: {result['url']}\n\nContent preview:\n{result['content'][:500]}..."
                return f"Could not fetch URL: {result.get('error', 'Unknown error')}"
        
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
        if "all crypto" in t or "crypto prices" in t:
            prices = CryptoPrices.get_all()
            result = "💰 Crypto Prices:\n\n"
            for p in prices:
                arrow = "📈" if p["change"] > 0 else "📉"
                result += f"{p['coin']}: ${p['price']:,} {arrow} {p['change']}%\n"
            return result
        
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
            elif "avax" in t: coin = "AVAX"
            elif "link" in t: coin = "LINK"
            elif "uni" in t: coin = "UNI"
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
        if "random number" in t or ("random" in t and "number" not in t):
            match = re.search(r"(\d+)\s+to\s+(\d+)", t)
            if match:
                min_v, max_v = int(match.group(1)), int(match.group(2))
                return f"🎲 Random number ({min_v}-{max_v}): {random.randint(min_v, max_v)}"
            return f"🎲 Random number (1-100): {random.randint(1, 100)}"
        
        # BMI
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
        
        # Age
        age_match = re.search(r"age\s+(?:of|from|born)?\s*(\d{4})", t)
        if age_match:
            birth_year = int(age_match.group(1))
            age = datetime.now().year - birth_year
            return f"🎂 Age: {age} years old"
        
        # Unit conversion
        if "convert" in t:
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
        if t.startswith("count "):
            text_to_count = text[6:]
            counts = TextTools.word_count(text_to_count)
            return f"📝 Word Count:\n\nWords: {counts['words']}\nCharacters: {counts['chars']}\nCharacters (no spaces): {counts['chars_no_spaces']}\nLines: {counts['lines']}"
        
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
            return f"🔒 Base64:\n{TextTools.base64_encode(text_to_encode)}"
        
        if "base64 decode" in t or "decode base64" in t:
            text_to_decode = text.split("decode ", 1)[1] if "decode " in t else text[12:]
            return f"🔓 Decoded:\n{TextTools.base64_decode(text_to_decode)}"
        
        if "md5" in t:
            text_to_hash = text.split("md5 ", 1)[1] if "md5 " in t else text[8:]
            return f"🔑 MD5:\n{TextTools.hash_md5(text_to_hash)}"
        
        if "sha256" in t:
            text_to_hash = text.split("sha256 ", 1)[1] if "sha256 " in t else text[11:]
            return f"🔑 SHA256:\n{TextTools.hash_sha256(text_to_hash)}"
        
        # QR Code
        if "qr" in t:
            text_for_qr = text.split("qr ", 1)[1] if "qr " in t else text.split("qrcode ", 1)[1] if "qrcode " in t else ""
            if text_for_qr:
                url = TextTools.qr_code_url(text_for_qr)
                return f"📱 QR Code for '{text_for_qr}':\n\n{url}\n\n(Open in browser to view)"
        
        # IP Address
        if t in ["ip", "my ip", "ip address"]:
            ip_info = WebAPIs.get_ip_info()
            if ip_info.get("success"):
                d = ip_info["data"]
                return f"🌐 Your IP Info:\n\nIP: {d.get('ip', 'N/A')}\nCity: {d.get('city', 'N/A')}\nRegion: {d.get('region', 'N/A')}\nCountry: {d.get('country_name', 'N/A')}\nISP: {d.get('org', 'N/A')}"
            return "🌐 IP: Could not fetch"
        
        # System info
        if t in ["system", "system info", "systeminfo"]:
            return f"💻 System Info:\n\nOS: {platform.system()}\nOS Version: {platform.version()}\nMachine: {platform.machine()}\nProcessor: {platform.processor()}\nPython: {platform.python_version()}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Voice - Speak
        if t.startswith("speak ") or "speak:" in t:
            text_to_speak = text.split("speak ", 1)[1] if text.startswith("speak ") else text.split("speak:", 1)[1] if "speak:" in text else ""
            if text_to_speak:
                success = VoiceAssistant.speak(text_to_speak)
                if success:
                    return f"🗣️ Speaking: {text_to_speak}"
                return "🗣️ Voice not available. Install pyttsx3 to enable."
        
        # Voice - Listen
        if t in ["listen", "voice input", "voice"]:
            text_heard = VoiceAssistant.listen()
            if text_heard:
                return f"🎤 Heard: {text_heard}"
            return "🎤 Voice input not available. Install speech_recognition to enable."
        
        # System Commands
        if "shutdown" in t:
            delay = int(re.findall(r"\d+", t)[0]) if re.findall(r"\d+", t) else 0
            return SystemCommands.shutdown(delay)
        
        if "restart" in t:
            delay = int(re.findall(r"\d+", t)[0]) if re.findall(r"\d+", t) else 0
            return SystemCommands.restart(delay)
        
        if "lock" in t:
            return SystemCommands.lock()
        
        if "sleep" in t:
            return SystemCommands.sleep()
        
        if "empty recycle" in t:
            return SystemCommands.empty_recycle_bin()
        
        # Password Generator (enhanced)
        if "generate password" in t or t.startswith("password "):
            length_match = re.search(r"(\d+)", t)
            length = int(length_match.group(1)) if length_match else 16
            pwd = PasswordGenerator.generate(min(length, 64), include_special=True)
            return f"🔐 Generated password ({len(pwd)} chars):\n{pwd}"
        
        # Clipboard
        if "clipboard" in t:
            if "copy" in t or "set" in t:
                copy_text = text.split("clipboard", 1)[1].replace("copy", "").replace("set", "").replace("to", "").strip()
                if copy_text:
                    ClipboardManager.copy(copy_text)
                    return f"📋 Copied to clipboard: {copy_text}"
            elif "paste" in t or "get" in t:
                content = ClipboardManager.paste()
                if content:
                    return f"📋 Clipboard content:\n{content}"
                return "📋 Clipboard is empty"
        
        # Screenshot
        if "screenshot" in t or "capture screen" in t:
            filename = Screenshot.capture()
            if filename:
                return f"📸 Screenshot saved: {filename}"
            return "📸 Screenshot not available. Install PIL to enable."
        
        # URL Shortener
        if "shorten url" in t or "url shortener" in t:
            url_match = re.search(r"(https?://[^\s]+|www\.[^\s]+)", text)
            if url_match:
                short_url = UrlShortener.shorten(url_match.group(1))
                if short_url:
                    return f"🔗 Short URL:\n{short_url}"
            return "Could not shorten URL"
        
        # Calendar Events
        if "add event" in t or "add calendar" in t:
            match = re.search(r"event\s+(.+?)(?:\s+on\s+|\s+at\s+|$)(.+?)(?:\s+at\s+(\d{1,2}:\d{2}))?$", t)
            if match:
                title = match.group(1).strip()
                date = match.group(2).strip() if match.group(2) else datetime.now().strftime("%Y-%m-%d")
                time = match.group(3) if match.group(3) else None
                cal = CalendarManager(self.config)
                cal.add_event(title, date, time)
                return f"📅 Event added: {title} on {date}"
            event_text = text.split("add event ", 1)[1] if "add event " in t else ""
            if event_text:
                cal = CalendarManager(self.config)
                cal.add_event(event_text, datetime.now().strftime("%Y-%m-%d"))
                return f"📅 Event added: {event_text}"
        
        if "calendar" in t or "show events" in t:
            cal = CalendarManager(self.config)
            events = cal.get_events()
            if events:
                result = "📅 Calendar Events:\n\n"
                for i, e in enumerate(events[-10:], 1):
                    result += f"{i}. {e['title']} - {e['date']}"
                    if e.get('time'):
                        result += f" at {e['time']}"
                    result += "\n"
                return result
            return "📅 No events. Say 'add event [title] on [date]'"
        
        # BMR Calculator
        if "bmr" in t:
            match = re.search(r"bmr\s+(\d+(?:\.\d+)?)\s*kg?\s+(\d+(?:\.\d+)?)\s*cm?\s+(\d+)\s*(male|female|m|f)?", t)
            if match:
                weight = float(match.group(1))
                height = float(match.group(2))
                age = int(match.group(3))
                gender = match.group(4) if match.group(4) else "male"
                bmr = HealthCalculator.bmr(weight, height, age, gender)
                return f"🔥 BMR (Basal Metabolic Rate):\n\nWeight: {weight}kg\nHeight: {height}cm\nAge: {age}\nGender: {gender}\nBMR: {bmr:.0f} calories/day"
        
        # TDEE Calculator
        if "tdee" in t:
            match = re.search(r"tdee\s+(\d+(?:\.\d+)?)\s+(sedentary|light|moderate|active|very\s*active)", t)
            if match:
                bmr = float(match.group(1))
                activity = match.group(2).replace(" ", "")
                tdee = HealthCalculator.tdee(bmr, activity)
                return f"🔥 TDEE (Total Daily Energy Expenditure):\n\nBMR: {bmr}\nActivity: {activity}\nTDEE: {tdee:.0f} calories/day"
        
        # AI Chat - Ask AI
        ai_trigger = ["ask ai", "chat with ai", "ai ", "ask gpt", "ask chatbot", "use ai", "deepseek", "llama"]
        if any(trigger in t for trigger in ai_trigger):
            message = text
            for trigger in ["ask ai ", "chat with ai ", "ai ", "ask gpt ", "ask chatbot ", "use ai ", "deepseek ", "llama "]:
                message = message.replace(trigger, "", 1)
            message = message.strip()
            
            provider = "torgpt"
            if "deepseek" in t:
                provider = "openrouter"
            elif "llama" in t:
                provider = "groq"
            
            api_key = self.config.get_key("openrouter") or self.config.get_key("groq") or ""
            
            result = FreeAIConnector.chat_with_ai(message, provider, api_key)
            if result.get("success"):
                return f"🤖 AI Response ({result.get('model', 'AI')}):\n\n{result['content']}"
            else:
                return f"❌ AI Error: {result.get('error', 'Connection failed')}\n\nTry again later or use a different provider."
        
        # Notes
        if "add note" in t:
            note = text.split("add note ", 1)[1] if "add note " in t else ""
            if note:
                notes = self.config.get("notes") or []
                notes.append({"text": note, "time": datetime.now().isoformat()})
                self.config.set("notes", notes)
                return f"📝 Note added: {note}"
        
        if t in ["notes", "list notes", "show notes"]:
            notes = self.config.get("notes") or []
            if notes:
                result = "📝 Your Notes:\n\n"
                for i, n in enumerate(notes[-10:], 1):
                    result += f"{i}. {n['text']}\n   ({n['time'][:10]})\n"
                return result
            return "📝 No notes yet. Say 'add note [text]'"
        
        # Todos
        if "add todo" in t or "add task" in t:
            todo = text.split("add todo ", 1)[1] if "add todo " in t else text.split("add task ", 1)[1] if "add task " in t else ""
            if todo:
                todos = self.config.get("todos") or []
                todos.append({"text": todo, "done": False, "time": datetime.now().isoformat()})
                self.config.set("todos", todos)
                return f"✅ Todo added: {todo}"
        
        if t in ["todos", "todo list", "show todos", "tasks"]:
            todos = self.config.get("todos") or []
            if todos:
                result = "📋 Your Todos:\n\n"
                for i, t in enumerate(todos[-10:], 1):
                    status = "✓" if t["done"] else "○"
                    result += f"{i}. [{status}] {t['text']}\n"
                result += "\nSay 'todo [number]' to toggle"
                return result
            return "📋 No todos. Say 'add todo [task]'"
        
        # Toggle todo
        todo_toggle = re.search(r"todo\s+(\d+)", t)
        if todo_toggle:
            idx = int(todo_toggle.group(1)) - 1
            todos = self.config.get("todos") or []
            if todos and 0 <= idx < len(todos):
                todos[idx]["done"] = not todos[idx]["done"]
                self.config.set("todos", todos)
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
            return "🪨📄✂️ Say 'rock', 'paper', or 'scissors'"
        
        # Number guessing
        if "guess number" in t:
            self.guess_number = random.randint(1, 100)
            self.guess_attempts = 0
            return "🎯 I'm thinking of a number 1-100. Say 'guess [number]'"
        
        guess_match = re.search(r"guess\s+(\d+)", t)
        if guess_match and self.guess_number is not None:
            self.guess_attempts += 1
            user_num = int(guess_match.group(1))
            if user_num == self.guess_number:
                result = f"🎉 Correct! You guessed {self.guess_number} in {self.guess_attempts} attempts!"
                self.guess_number = None
                self.guess_attempts = 0
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
                "bear": "ʕ•ᴥ•ʔ",
                "dog": "▬▬▬▬▬●▬▬▬▬▬",
            }
            result = "🎨 ASCII Art:\n\n"
            for name, art in arts.items():
                result += f"{name}: {art}\n"
            return result
        
        # Emoji meanings
        if "emoji" in t and "meaning" in t:
            meanings = {
                "😊": "Smiling Eyes - Joy",
                "😂": "Tears of Joy - Laughing",
                "❤️": "Red Heart - Love",
                "👍": "Thumbs Up - Like",
                "🎉": "Party Popper - Celebrate",
                "🔥": "Fire - Hot/Trendy",
                "💀": "Skull - Dead/Funny",
                "🤔": "Thinking",
                "😎": "Cool",
                "😭": "Crying",
            }
            result = "😀 Emoji Meanings:\n\n"
            for emo, mean in meanings.items():
                result += f"{emo} = {mean}\n"
            return result
        
        # Personality switch
        if "personality" in t:
            if "set" in t or "change" in t:
                for p in Personalities.PERSONALITIES:
                    if p in t:
                        self.personality = p
                        self.config.set("personality", p)
                        return f"✅ Personality changed to {Personalities.PERSONALITIES[p]['name']}!"
            result = "🎭 Available Personalities:\n\n"
            for k, v in Personalities.PERSONALITIES.items():
                result += f"• {v['name']}: {v['description']}\n"
            result += "\nSay 'personality set [name]' to change"
            return result
        
        # Clear history
        if "clear history" in t or "clear memory" in t:
            self.memory.clear()
            return "🗑️ Conversation history cleared!"
        
        # Export chat
        if "export" in t and "chat" in t:
            filename = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.memory.save_to_file(filename)
            return f"💾 Chat exported to {filename}"
        
        # Import chat
        if "import" in t and "chat" in t:
            return "📂 Say 'import chat [filename]' to load a saved conversation"
        
        # Search history
        if "search history" in t:
            query = text.split("search history ", 1)[1] if "search history " in t else ""
            if query:
                results = self.memory.search(query)
                if results:
                    result = f"🔍 Found {len(results)} matches:\n\n"
                    for r in results[:5]:
                        result += f"• {r['content'][:80]}...\n"
                    return result
                return "No matches found"
        
        # Summarize
        if "summarize" in t and "conversation" in t:
            recent = self.memory.get_recent(10)
            if len(recent) > 1:
                result = "📝 Conversation Summary:\n\n"
                result += f"Total messages: {len(recent)}\n"
                result += f"First message: {recent[0]['content'][:50]}...\n"
                result += f"Last message: {recent[-1]['content'][:50]}...\n"
                return result
            return "Not enough history to summarize"
        
        # Stock prices
        if t.startswith("stock ") or "stock price" in t:
            symbol = re.search(r"(?:stock |stock price )?([a-z]+)", t)
            if symbol:
                s = symbol.group(1).upper()
                result = StockPrices.get_price(s)
                if result.get("success"):
                    arrow = "📈" if result["change"] > 0 else "📉"
                    return f"📈 {result['symbol']}: ${result['price']:.2f} {arrow} {result['change']}%"
                return f"Unknown stock symbol: {s}. Try: AAPL, GOOGL, MSFT, AMZN, TSLA, META, NVDA, AMD, NFLX, DIS"
        
        if "all stocks" in t or "stock list" in t:
            stocks = StockPrices.get_all()
            result = "📈 Stock Prices:\n\n"
            for s in stocks:
                arrow = "📈" if s["change"] > 0 else "📉"
                result += f"{s['symbol']}: ${s['price']:.2f} {arrow} {s['change']}%\n"
            return result
        
        # Color converter
        if "color" in t and ("convert" in t or "hex" in t or "rgb" in t):
            hex_match = re.search(r"#?([0-9a-fA-F]{6})", t)
            if hex_match:
                rgb = ColorConverter.hex_to_rgb(hex_match.group(1))
                if rgb:
                    hsl = ColorConverter.rgb_to_hsl(*rgb)
                    hex_val = ColorConverter.rgb_to_hex(*rgb)
                    return f"🎨 Color Converter:\n\nHex: #{hex_match.group(1).upper()}\nRGB: rgb({rgb[0]}, {rgb[1]}, {rgb[2]})\nHSL: hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%)"
        
        # NASA Picture of the Day
        if "nasa" in t or "space photo" in t or "apod" in t:
            result = WebAPIs.get_nasa_apod(self.config.get_key("nasa"))
            if result.get("success"):
                return f"🌌 NASA Picture of the Day:\n\n{result['title']}\n\n{result['explanation']}\n\n🔗 {result.get('url', '')}"
        
        # GitHub user info
        if "github" in t and "user" in t or t.startswith("github "):
            match = re.search(r"github\s+(\w+)", t)
            if match:
                username = match.group(1)
                result = WebAPIs.get_github_user(username)
                if result.get("success"):
                    return f"👤 GitHub User: {result['login']}\n\nName: {result.get('name', 'N/A')}\nBio: {result.get('bio', 'N/A')}\nRepos: {result.get('public_repos', 0)}\nFollowers: {result.get('followers', 0)}\nFollowing: {result.get('following', 0)}"
        
        # Translation
        if "translate" in t:
            match = re.search(r"translate\s+(.+?)\s+to\s+(\w+)", t)
            if match:
                text_to_translate = match.group(1)
                target_lang = match.group(2)
                result = Translator.translate(text_to_translate, target_lang)
                return f"🌍 Translation to {target_lang.upper()}:\n\n{result}"
        
        # Math solver
        if "solve" in t or "math" in t:
            match = re.search(r"(?:solve|math)\s+(.+)", t)
            if match:
                expr = match.group(1)
                result = MathSolver.solve(expr)
                if result:
                    return f"🧮 Solution: {result}"
        
        # Quadratic equation
        if "quadratic" in t or "roots" in t:
            match = re.search(r"(\-?\d+)\s*x\s*[\^2]?\s*[+\-]\s*(\-?\d+)\s*x\s*[+\-]\s*(\-?\d+)\s*=\s*0", t)
            if match:
                a, b, c = int(match.group(1)), int(match.group(2)), int(match.group(3))
                result = MathSolver.solve_quadratic(a, b, c)
                return f"🧮 Quadratic Equation: {a}x² + {b}x + {c} = 0\n\nSolutions: {result}"
        
        # Open website
        if t.startswith("open ") or "open website" in t:
            match = re.search(r"open\s+(.+)", t)
            if match:
                site = match.group(1).strip()
                if not site.startswith("http"):
                    site = "https://" + site
                try:
                    webbrowser.open(site)
                    return f"🌐 Opening: {site}"
                except:
                    return f"Could not open: {site}"
        
        # Countdown timer
        if "countdown" in t or "timer" in t:
            match = re.search(r"(\d+)\s*(?:second|min|hour)", t)
            if match:
                return f"⏱️ Timer set for {match.group(1)}! (Note: Actual timer requires GUI integration)"
        
        # Word of the day
        if "word of the day" in t or "daily word" in t:
            words = ["serendipity", "ephemeral", "eloquent", "resilient", "enigma", "wanderlust", "petrichor", "sonder", "euphoria", "halcyon"]
            word = random.choice(words)
            definition = WebAPIs.define_word(word)
            if definition.get("success"):
                return f"📝 Word of the Day: {definition['word']}\n\n({definition.get('phonetic', '')})\n\n{definition['definitions'][0]['def']}"
        
        # Leap year check
        if "leap year" in t:
            match = re.search(r"(\d{4})", t)
            if match:
                year = int(match.group(1))
                is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                return f"📅 {year} is {'a leap year' if is_leap else 'not a leap year'}"
        
        # Age calculator
        if "age" in t and "born" in t:
            match = re.search(r"born\s+(\d{4})", t)
            if match:
                year = int(match.group(1))
                age = datetime.now().year - year
                return f"🎂 Age: {age} years old"
        
        # Day of week
        if "day of week" in t or "what day" in t:
            match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", t)
            if match:
                try:
                    d = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                    return f"📅 {d.strftime('%A, %B %d, %Y')}"
                except:
                    pass
        
        # Country info
        if "country" in t or t.startswith("info "):
            match = re.search(r"(?:country |info )?(.+)", t)
            if match:
                country = match.group(1).strip()
                if country and len(country) > 2:
                    result = WebAPIs.get_country_info(country)
                    if result.get("success"):
                        return f"🌍 {result['name']}\n\nCapital: {result.get('capital', 'N/A')}\nRegion: {result.get('region', 'N/A')}\nPopulation: {result.get('population', 0):,}\nCurrency: {result.get('currency', 'N/A')}\nLanguages: {result.get('languages', 'N/A')}"
        
        # Reminders
        if "remind" in t and "add" in t:
            match = re.search(r"remind me to (.+)", t)
            if match:
                reminder_text = match.group(1)
                reminders = self.config.get("reminders") or []
                reminders.append({"text": reminder_text, "created": datetime.now().isoformat()})
                self.config.set("reminders", reminders)
                return f"⏰ Reminder added: {reminder_text}"
        
        if t in ["reminders", "list reminders", "show reminders"]:
            reminders = self.config.get("reminders") or []
            if reminders:
                result = "⏰ Your Reminders:\n\n"
                for i, r in enumerate(reminders, 1):
                    result += f"{i}. {r['text']}\n"
                return result
            return "⏰ No reminders. Say 'remind me to [task]'"
        
        # Run Python code safely
        if t.startswith("python ") or t.startswith("run "):
            code = text.split("python ", 1)[1] if "python " in t else text.split("run ", 1)[1]
            result = CodeExecutor.execute_python(code)
            return f"💻 Output:\n{result}"
        
        # List files
        if "list files" in t or "files in" in t:
            match = re.search(r"files in (.+)", t)
            if match:
                folder = match.group(1).strip()
                files = FileManager.list_files(folder)
            else:
                files = FileManager.list_files(".")
            if files:
                return f"📁 Files:\n\n" + "\n".join(f"• {f}" for f in files[:20])
            return "📁 No files found"
        
        # === NEW FREE API COMMANDS ===
        
        # Cat fact
        if t in ["cat fact", "cat facts"]:
            result = WebAPIs.get_cat_fact()
            if result.get("success"):
                return f"🐱 Cat Fact:\n\n{result['fact']}"
            return "Could not fetch cat fact"
        
        # Dog fact
        if t in ["dog fact", "dog facts"]:
            result = WebAPIs.get_dog_fact()
            if result.get("success"):
                return f"🐕 Dog Fact:\n\n{result['fact']}"
            return "Could not fetch dog fact"
        
        # Trivia
        if t in ["trivia", "new trivia", "random trivia"]:
            categories = ["science", "history", "geography", "art", "sports", "general"]
            cat = random.choice(categories)
            result = WebAPIs.get_trivia(cat)
            if result.get("success"):
                self._trivia_question = result
                answers = result["incorrect"] + [result["correct"]]
                random.shuffle(answers)
                return f"❓ Trivia ({cat}):\n\n{result['question']}\n\n" + "\n".join(f"{i+1}. {a}" for i, a in enumerate(answers))
            return "Could not fetch trivia"
        
        # Answer trivia
        if hasattr(self, '_trivia_question') and self._trivia_question and t[0].isdigit():
            return "Trivia answered! Say 'new trivia' for another question."
        
        # Gender prediction
        if "gender" in t:
            match = re.search(r"gender\s+(\w+)", t)
            if match:
                name = match.group(1)
                result = WebAPIs.predict_gender(name)
                if result.get("success"):
                    return f"👤 Gender Prediction for '{result['name']}':\n\nGender: {result['gender']}\nProbability: {result['probability']*100:.0f}%"
        
        # Age prediction
        if "age" in t and "predict" in t:
            match = re.search(r"predict.*?age\s+(\w+)", t)
            if not match:
                match = re.search(r"age\s+of\s+(\w+)", t)
            if match:
                name = match.group(1)
                result = WebAPIs.predict_age(name)
                if result.get("success"):
                    return f"🎂 Predicted Age for '{result['name']}':\n\nAge: {result['age']}\nRecords found: {result['count']}"
        
        # Nationality prediction
        if "nationality" in t or "where from" in t:
            match = re.search(r"(?:nationality|where from)\s+(\w+)", t)
            if match:
                name = match.group(1)
                result = WebAPIs.predict_nationality(name)
                if result.get("success"):
                    countries = result.get("countries", [])
                    if countries:
                        result_text = f"🌍 Nationality Prediction for '{result['name']}':\n\n"
                        for c in countries:
                            result_text += f"• {c.get('country_id', 'N/A')}: {c.get('probability', 0)*100:.1f}%\n"
                        return result_text
        
        # Random user
        if "random user" in t or "generate user" in t:
            result = WebAPIs.get_random_user()
            if result.get("success"):
                return f"👤 Random User:\n\nName: {result['name']}\nEmail: {result['email']}\nLocation: {result['location']}\nPhone: {result['phone']}"
        
        # Number fact
        if "number fact" in t or "fact about" in t:
            match = re.search(r"(\d+)", t)
            num = int(match.group(1)) if match else None
            result = WebAPIs.get_number_fact(num)
            if result.get("success"):
                return f"🔢 Fact about {result['number']}:\n\n{result['fact']}"
        
        # Exchange rate
        if "exchange rate" in t or "rate" in t and "to" in t:
            match = re.search(r"(\w+)\s+to\s+(\w+)", t)
            if match:
                from_c, to_c = match.group(1), match.group(2)
                result = WebAPIs.get_exchange_rate(from_c, to_c)
                if result.get("success"):
                    return f"💱 Exchange Rate:\n\n1 {result['from']} = {result['rate']:.4f} {result['to']}"
        
        # Holidays
        if "holidays" in t or "holiday" in t:
            match = re.search(r"(\d{4})", t)
            year = int(match.group(1)) if match else datetime.now().year
            result = WebAPIs.get_holidays(year)
            if result.get("success"):
                result_text = f"🎄 Holidays {year} (US):\n\n"
                for h in result["holidays"]:
                    result_text += f"• {h['date']}: {h['name']}\n"
                return result_text
        
        # Quote of the day
        if "quote of the day" in t or "daily quote" in t:
            result = WebAPIs.get_quote()
            if result.get("success"):
                return f"💭 Quote of the Day:\n\n\"{result['quote']}\"\n\n— {result['author']}"
        
        # === WEB SEARCH COMMAND ===
        if "search" in t or "google" in t or "look up" in t:
            # Extract search query
            query = text
            for prefix in ["search ", "search for ", "google ", "look up "]:
                if query.lower().startswith(prefix):
                    query = query[len(prefix):]
                    break
            # Remove "on google" or similar suffixes
            for suffix in [" on google", " on web", " online"]:
                if query.lower().endswith(suffix):
                    query = query[:-len(suffix)]
            query = query.strip()
            
            if query and len(query) > 1:
                result = WebAPIs.web_search(query, 5)
                if result.get("success"):
                    response = f"🔍 Search results for '{result['query']}':\n\n"
                    for i, r in enumerate(result["results"], 1):
                        response += f"{i}. {r['title']}\n"
                        response += f"   {r['url']}\n"
                        if r.get("snippet"):
                            response += f"   {r['snippet'][:80]}...\n"
                        response += "\n"
                    return response
                return "Search failed. Please try again."
        
        # AI Chat response (use generator for better responses)
        return AIResponseGenerator.generate_response(text, self.personality)
    
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
        
        if "answer" in t and self.guess_number is None:
            return "No riddle active. Say 'riddle' for a new one!"
        
        if "would you" in t:
            q = random.choice(Entertainment.WOULD_YOU_RATHER)
            return f"🤔 {q[0]}\n\n{q[1]}"
        
        return "I'm not sure what entertainment you're looking for!"
    
    def _handle_chat(self, text: str) -> str:
        t = text.lower()
        
        # Name
        if "my name is" in t:
            match = re.search(r"my name is (.+)", t)
            if match:
                self.user_name = match.group(1).strip().capitalize()
                self.config.set("user_name", self.user_name)
                return f"Nice to meet you, {self.user_name}! I'll remember that."
        
        name_prefix = f"{self.user_name}, " if self.user_name else ""
        
        # Greetings
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
            return "Say 'weather [city]' to get weather!"
        
        if t in ["help", "commands", "what can you do"]:
            return self._get_help()
        
        # Check knowledge base
        kb_result = self.knowledge.get(t)
        if kb_result:
            return kb_result
        
        # Default responses
        responses = [
            f"{name_prefix}That's interesting! Tell me more or ask me a question!",
            f"{name_prefix}I'm not sure how to respond. Try asking me something!",
            f"{name_prefix}Got it! Need help with something specific?",
            f"{name_prefix}Hmm, let me think... Just ask me anything!",
        ]
        return random.choice(responses)
    
    def _get_help(self) -> str:
        return """🤖 AI Assistant PRO v12 - ALL COMMANDS:

📝 QUESTIONS:
• What is [topic]?
• Who is [person]?
• Define [word]
• How to [something]
• Where is [place]?
• When did [event]?

🔧 UTILITIES:
• weather [city] • news
• calculate [math] • solve [expression]
• password [length] • uuid
• time • date • datetime
• convert [num] [from] to [to]
• exchange rate [USD] to [EUR]
• crypto [coin] • all crypto
• stock [symbol] • all stocks

🎲 RANDOM:
• dice • dice 2d20
• coin flip
• random [1] to [100]
• random user

📊 HEALTH:
• bmi [weight]kg [height]cm
• tip [amount] at [X]%

📅 TIME:
• age [birth year]
• leap year [year]
• day of week [YYYY-MM-DD]
• holidays [2024]

📝 TEXT TOOLS:
• count [text]
• reverse [text]
• uppercase [text]
• lowercase [text]
• base64 encode [text]
• base64 decode [text]
• md5 [text]
• sha256 [text]
• qr [text]

🎨 CONVERTERS:
• color #hexcode
• translate [text] to [language]

🌐 WEB APIs:
• nasa • space photo
• github [username]
• country [name]
• open [website]

🔮 PREDICTIONS:
• gender [name]
• predict age [name]
• nationality [name]

🐱🐕 FACTS:
• cat fact
• dog fact
• number fact [42]
• trivia

💭 QUOTES:
• quote of the day
• joke • fact • quote

📋 PRODUCTIVITY:
• add note [text] • notes
• add todo [task] • todos
• todo [number] (toggle)
• remind me to [task]

💾 HISTORY:
• search history [query]
• clear history
• export chat

🎮 GAMES:
• rock / paper / scissors
• guess number

🎭 PERSONALITY:
• personality
• personality set [name]

💬 CHAT:
• Tell me your name!
• Ask me anything!

🌟 TRY THESE NEW ONES:
• random user
• gender john
• nationality elon
• holidays 2025
• quote of the day"""


# ==================== GUI ====================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant PRO v12")
        self.root.geometry("1200x800")
        self.root.minsize(900, 650)
        
        # Modern dark theme palette
        self.colors = {
            "bg_main": "#0a0e14",
            "bg_sidebar": "#0d1117",
            "bg_chat": "#11161d",
            "bg_input": "#161b22",
            "bg_hover": "#1f2937",
            "bg_card": "#1a1f29",
            "text": "#e6edf3",
            "text_dim": "#7d8590",
            "text_bright": "#f0f6fc",
            "green": "#3fb950",
            "green_dim": "#238636",
            "blue": "#58a6ff",
            "blue_dim": "#1f6feb",
            "purple": "#a78bfa",
            "purple_dim": "#8250df",
            "orange": "#d29922",
            "orange_dim": "#9e6a03",
            "red": "#f85149",
            "cyan": "#39c5cf",
            "pink": "#db61a2",
            "border": "#30363d",
            "highlight": "#388bfd",
        }
        
        self.root.configure(bg=self.colors["bg_main"])
        self.ai = ProAI()
        
        self._setup_ui()
        self._welcome()
    
    def _setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors["bg_main"])
        main_container.pack(fill="both", expand=True)
        
        # Left Sidebar
        sidebar = tk.Frame(main_container, bg=self.colors["bg_sidebar"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo section
        logo_frame = tk.Frame(sidebar, bg=self.colors["bg_sidebar"], pady=20, padx=15)
        logo_frame.pack(fill="x")
        
        tk.Label(logo_frame, text="◈", font=("Segoe UI", 32), bg=self.colors["bg_sidebar"], 
                fg=self.colors["green"]).pack()
        tk.Label(logo_frame, text="AI Assistant", font=("Segoe UI", 18, "bold"), 
                bg=self.colors["bg_sidebar"], fg=self.colors["text_bright"]).pack(pady=(5, 0))
        tk.Label(logo_frame, text="PRO v12", font=("Segoe UI", 9), 
                bg=self.colors["bg_sidebar"], fg=self.colors["green"]).pack()
        
        # Quick actions section
        tk.Label(sidebar, text="QUICK ACTIONS", font=("Segoe UI", 8, "bold"), 
                bg=self.colors["bg_sidebar"], fg=self.colors["text_dim"], 
                padx=15, pady=15, anchor="w").pack(fill="x")
        
        quick_actions = [
            ("🤖", "AI", self._quick_action),
            ("🌐", "Search", lambda: self._quick_search()),
            ("📰", "News", lambda: self._quick_cmd("news")),
            ("💰", "Crypto", lambda: self._quick_cmd("all crypto")),
            ("🎲", "Trivia", lambda: self._quick_cmd("trivia")),
            ("😂", "Joke", lambda: self._quick_cmd("joke")),
            ("📖", "Wiki", lambda: self._quick_wiki()),
            ("🌤️", "Weather", lambda: self._quick_weather()),
        ]
        
        for icon, label, cmd in quick_actions:
            btn = tk.Frame(sidebar, bg=self.colors["bg_sidebar"], cursor="hand2")
            btn.pack(fill="x", padx=10, pady=2)
            btn.bind("<Button-1>", lambda e, c=cmd: c() if callable(c) else None)
            btn.bind("<Enter>", lambda e, w=btn: w.config(bg=self.colors["bg_hover"]))
            btn.bind("<Leave>", lambda e, w=btn: w.config(bg=self.colors["bg_sidebar"]))
            
            tk.Label(btn, text=icon, font=("Segoe UI", 14), bg=self.colors["bg_sidebar"], 
                    width=3, anchor="e").pack(side="left", fill="y")
            tk.Label(btn, text=label, font=("Segoe UI", 11), bg=self.colors["bg_sidebar"], 
                    fg=self.colors["text"], anchor="w").pack(side="left", fill="both", expand=True, ipady=8)
        
        # Stats section
        stats_frame = tk.Frame(sidebar, bg=self.colors["bg_card"], padx=15, pady=15)
        stats_frame.pack(side="bottom", fill="x", padx=10, pady=15)
        
        tk.Label(stats_frame, text="Session Stats", font=("Segoe UI", 9, "bold"), 
                bg=self.colors["bg_card"], fg=self.colors["text_dim"]).pack(anchor="w", pady=(10, 5))
        
        self.stat_messages = tk.Label(stats_frame, text="Messages: 0", 
                font=("Segoe UI", 10), bg=self.colors["bg_card"], fg=self.colors["text"])
        self.stat_messages.pack(anchor="w", pady=5)
        
        self.stat_time = tk.Label(stats_frame, text="Started: --", 
                font=("Segoe UI", 10), bg=self.colors["bg_card"], fg=self.colors["text"])
        self.stat_time.pack(anchor="w")
        
        # Right content area
        content = tk.Frame(main_container, bg=self.colors["bg_main"])
        content.pack(side="left", fill="both", expand=True)
        
        # Header bar
        header = tk.Frame(content, bg=self.colors["bg_main"], padx=20, pady=15)
        header.pack(fill="x")
        
        title_area = tk.Frame(header, bg=self.colors["bg_main"])
        title_area.pack(side="left")
        
        tk.Label(title_area, text="Chat", font=("Segoe UI", 22, "bold"), 
                bg=self.colors["bg_main"], fg=self.colors["text_bright"]).pack(anchor="w")
        tk.Label(title_area, text="Ask anything, use commands, or just chat", 
                font=("Segoe UI", 10), bg=self.colors["bg_main"], fg=self.colors["text_dim"]).pack(anchor="w")
        
        # Header buttons
        header_btns = tk.Frame(header, bg=self.colors["bg_main"])
        header_btns.pack(side="right")
        
        header_buttons = [
            ("New Chat", self._new_chat, self.colors["blue_dim"]),
            ("Settings", self._settings, self.colors["orange_dim"]),
            ("Export", self._export_chat, self.colors["purple_dim"]),
            ("Clear", self._clear, self.colors["red"]),
        ]
        
        for text, cmd, color in header_buttons:
            btn = tk.Button(header_btns, text=text, command=cmd, 
                           bg=color, fg="white", font=("Segoe UI", 9, "bold"),
                           relief="flat", padx=16, pady=8, cursor="hand2", bd=0)
            btn.pack(side="left", padx=4)
        
        # Chat display with rounded look
        chat_frame = tk.Frame(content, bg=self.colors["bg_chat"], padx=2, pady=2)
        chat_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.chat = scrolledtext.ScrolledText(
            chat_frame, bg=self.colors["bg_chat"], fg=self.colors["text"],
            font=("Segoe UI", 12), relief="flat", wrap="word",
            padx=20, pady=18, highlightthickness=0, bd=0
        )
        self.chat.pack(fill="both", expand=True)
        
        # Chat tags for different message types
        self.chat.tag_config("user", foreground=self.colors["blue"], spacing1=15, lmargin1=20, lmargin2=20, 
                            font=("Segoe UI", 12, "bold"))
        self.chat.tag_config("ai", foreground=self.colors["green"], spacing1=15, lmargin1=20, lmargin2=20)
        self.chat.tag_config("system", foreground=self.colors["text_dim"], spacing1=8, 
                            font=("Segoe UI", 10, "italic"))
        self.chat.tag_config("header", foreground=self.colors["text_bright"], spacing1=20, 
                            font=("Segoe UI", 12, "bold"))
        
        # Input area with modern styling
        input_container = tk.Frame(content, bg=self.colors["bg_input"], padx=15, pady=12)
        input_container.pack(fill="x", padx=15, pady=(0, 15))
        
        # Input wrapper with border
        input_wrap = tk.Frame(input_container, bg=self.colors["border"], padx=2, pady=2)
        input_wrap.pack(fill="x")
        
        self.entry = tk.Entry(
            input_wrap, bg=self.colors["bg_input"], fg=self.colors["text"],
            font=("Segoe UI", 13), relief="flat", insertbackground=self.colors["green"],
            bd=0, highlightthickness=0
        )
        self.entry.pack(fill="x", ipady=14, padx=10)
        self.entry.bind("<Return>", self._send)
        self.entry.bind("<KP_Enter>", self._send)
        
        # Send button
        send_btn = tk.Button(
            input_wrap, text="➤ Send", command=self._send,
            bg=self.colors["green_dim"], fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", padx=24, pady=10, cursor="hand2", bd=0
        )
        send_btn.pack(side="right", padx=2, pady=2)
        
        # Hint text
        tk.Label(input_container, text="Press Enter to send • Try 'help' for commands", 
                font=("Segoe UI", 9), bg=self.colors["bg_input"], 
                fg=self.colors["text_dim"]).pack(pady=(8, 0))
        
        # Status bar
        status_bar = tk.Frame(content, bg=self.colors["bg_card"], padx=20, pady=8)
        status_bar.pack(fill="x")
        
        self.status = tk.Label(status_bar, text="● Ready", 
                bg=self.colors["bg_card"], fg=self.colors["green"],
                font=("Segoe UI", 9), anchor="w")
        self.status.pack(side="left")
        
        tk.Label(status_bar, text="|", bg=self.colors["bg_card"], fg=self.colors["border"]).pack(side="left", padx=10)
        
        self.persona_label = tk.Label(status_bar, text=f"Personality: {self.ai.personality}", 
                bg=self.colors["bg_card"], fg=self.colors["text_dim"], font=("Segoe UI", 9))
        self.persona_label.pack(side="left")
        
    def _quick_action(self):
        self.entry.focus_set()
        
    def _quick_search(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, "search ")
        self.entry.focus_set()
        
    def _quick_wiki(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, "wiki ")
        self.entry.focus_set()
        
    def _quick_weather(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, "weather ")
        self.entry.focus_set()
        
    def _quick_cmd(self, cmd):
        self.entry.delete(0, "end")
        self.entry.insert(0, cmd)
        self._send()
        
    def _new_chat(self):
        self._clear()
        
    def _welcome(self):
        self._add("header", "👋 Welcome to AI Assistant PRO v12!\n", "header")
        self._add("AI", """🎯 Your Ultimate AI Companion

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ What I can do:
• Answer ANY question using web search & Wikipedia
• 50+ commands (weather, crypto, stocks, news, etc.)
• Remember our conversation
• Multiple personalities
• Text tools (hash, QR, encode, etc.)
• Games & entertainment
• And much more!

🚀 Quick Start:
• Type naturally - I'll understand!
• "weather London" - Get weather
• "search Python" - Web search  
• "joke" - Get a laugh
• "all crypto" - Crypto prices
• "help" - Full command list
• "personality" - Change my style

Let's chat! 🚀""", "ai")
    
    def _send(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        
        self.entry.delete(0, "end")
        self._add(f"user", f"You: ", "user")
        self._add(f"", text + "\n\n", "user")
        self.status.config(text="◐ Thinking...")
        self.root.update()
        
        threading.Thread(target=self._respond, args=(text,), daemon=True).start()
    
    def _respond(self, text: str):
        try:
            response = self.ai.chat(text)
            self.root.after(0, lambda: self._add("assistant", f"AI: ", "ai"))
            self.root.after(0, lambda: self._add("", response + "\n\n", "ai"))
            self.root.after(0, lambda: self.status.config(text="● Ready"))
            self.root.after(0, lambda: self._update_stats())
        except Exception as e:
            self.root.after(0, lambda: self._add("error", f"Error: {str(e)}\n", "system"))
            self.root.after(0, lambda: self.status.config(text="● Error occurred"))
    
    def _update_stats(self):
        self.stat_messages.config(text=f"Messages: {self.ai.conv_count}")
        
    def _add(self, sender: str, message: str, tag: str):
        self.chat.config(state="normal")
        self.chat.insert("end", f"{sender} {message}\n", tag)
        self.chat.see("end")
        self.chat.config(state="disabled")
    
    def _clear(self):
        self.chat.config(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.config(state="disabled")
        self._welcome()
    
    def _help(self):
        self._add("AI", self.ai._get_help(), "ai")
    
    def _settings(self):
        self._add("AI", f"""⚙️ SETTINGS

Current:
• Personality: {self.ai.personality}
• Username: {self.ai.user_name or 'Not set'}
• Messages: {self.ai.conv_count}
• History: {len(self.ai.memory.messages)} messages

Commands:
• 'personality set helpful' - Friendly assistant
• 'personality set professional' - Business style
• 'personality set creative' - Artistic writer
• 'personality set tech' - Tech expert
• 'personality set funny' - Comedian
• 'my name is [name]' - Set your name
• 'clear history' - Clear memory
• 'search history [query]' - Find messages""", "ai")
    
    def _export_chat(self):
        filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            self.ai.memory.save_to_file(filename)
            self._add("AI", f"💾 Chat exported to: {filename}", "ai")
        except Exception as e:
            self._add("AI", f"Export failed: {str(e)}", "system")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
