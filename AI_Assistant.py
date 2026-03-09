#!/usr/bin/env python3
"""
AI Assistant - All-in-One Artificial Intelligence Assistant
Version: 6.0 - WITH API CONNECTIONS
Author: AI Assistant
License: Free
"""

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, filedialog
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
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict


# ==================== API CONNECTORS ====================

class APIConfig:
    """Configuration for API keys"""
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
        return {
            "openweather": "",
            "newsapi": "",
            "openai": ""
        }
    
    def save_keys(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.keys, f, indent=2)
    
    def get(self, key: str) -> str:
        return self.keys.get(key, "")
    
    def set(self, key: str, value: str):
        self.keys[key] = value
        self.save_keys()


class WikipediaAPI:
    """Free Wikipedia API - no key required"""
    
    @staticmethod
    def search(query: str, limit: int = 5) -> Dict:
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit={limit}&format=json"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/6.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            if len(data) >= 2:
                return {
                    "success": True,
                    "results": [{"title": data[1][i], "description": data[2][i], "url": data[3][i]} 
                               for i in range(len(data[1]))]
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False, "error": "No results"}
    
    @staticmethod
    def get_summary(topic: str) -> Dict:
        try:
            ssl_context = ssl.create_default_context()
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/6.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            return {
                "success": True,
                "title": data.get("title", ""),
                "description": data.get("extract", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class WeatherAPI:
    """OpenWeatherMap API - requires API key"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_weather(self, city: str) -> Dict:
        if not self.api_key:
            return self._mock_weather(city)
        
        try:
            url = f"{self.base_url}/weather?q={urllib.parse.quote(city)}&appid={self.api_key}&units=metric"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/6.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            return {
                "success": True,
                "city": data["name"],
                "country": data["sys"]["country"],
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"]
            }
        except Exception as e:
            return self._mock_weather(city)
    
    def get_forecast(self, city: str, days: int = 5) -> Dict:
        if not self.api_key:
            return {"success": True, "forecast": [{"day": i+1, "temp": random.randint(10, 30), "condition": random.choice(["sunny", "cloudy", "rainy"])} for i in range(days)]}
        
        try:
            url = f"{self.base_url}/forecast?q={urllib.parse.quote(city)}&appid={self.api_key}&units=metric&cnt={days*8}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/6.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            forecasts = []
            for i, item in enumerate(data["list"]):
                if i % 8 == 0:
                    forecasts.append({
                        "day": len(forecasts) + 1,
                        "temp": item["main"]["temp"],
                        "description": item["weather"][0]["description"]
                    })
            
            return {"success": True, "forecast": forecasts}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _mock_weather(self, city: str) -> Dict:
        return {
            "success": True,
            "city": city,
            "country": "XX",
            "temp": random.randint(5, 35),
            "feels_like": random.randint(5, 35),
            "humidity": random.randint(30, 90),
            "description": random.choice(["clear sky", "few clouds", "scattered clouds", "rain", "overcast"]),
            "source": "mock"
        }


class NewsAPI:
    """News API - requires API key"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
    
    def get_top_headlines(self, category: str = "general", country: str = "us") -> Dict:
        if not self.api_key:
            return self._mock_news()
        
        try:
            url = f"{self.base_url}/top-headlines?country={country}&category={category}&apiKey={self.api_key}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/6.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            articles = []
            for article in data.get("articles", [])[:10]:
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "url": article.get("url", ""),
                    "published": article.get("publishedAt", "")
                })
            
            return {"success": True, "articles": articles}
        except Exception as e:
            return self._mock_news()
    
    def search_news(self, query: str) -> Dict:
        if not self.api_key:
            return self._mock_news(query)
        
        try:
            url = f"{self.base_url}/everything?q={urllib.parse.quote(query)}&apiKey={self.api_key}&sortBy=relevancy&pageSize=10"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/6.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            articles = []
            for article in data.get("articles", [])[:10]:
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "url": article.get("url", "")
                })
            
            return {"success": True, "articles": articles}
        except Exception as e:
            return self._mock_news(query)
    
    def _mock_news(self, query: str = "") -> Dict:
        topics = ["technology", "science", "business", "sports", "entertainment"]
        topic = query if query else random.choice(topics)
        
        return {
            "success": True,
            "source": "mock",
            "articles": [
                {
                    "title": f"Latest {topic.title()} News Headline {i+1}",
                    "description": f"This is a sample news article about {topic} for demonstration purposes.",
                    "source": "Demo News",
                    "url": "https://example.com"
                }
                for i in range(5)
            ]
        }


class DictionaryAPI:
    """Free Dictionary API - no key required"""
    
    @staticmethod
    def lookup(word: str) -> Dict:
        try:
            ssl_context = ssl.create_default_context()
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/6.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            if isinstance(data, list) and len(data) > 0:
                entry = data[0]
                meanings = []
                for meaning in entry.get("meanings", [])[:2]:
                    for defn in meaning.get("definitions", [])[:2]:
                        meanings.append({
                            "part_of_speech": meaning.get("partOfSpeech", ""),
                            "definition": defn.get("definition", "")
                        })
                
                return {
                    "success": True,
                    "word": entry.get("word", ""),
                    "phonetic": entry.get("phonetic", ""),
                    "meanings": meanings
                }
        except Exception as e:
            pass
        
        return {"success": False, "error": "Word not found"}


class JokeAPI:
    """Free Joke APIs - no key required"""
    
    @staticmethod
    def get_joke(category: str = "any") -> Dict:
        try:
            ssl_context = ssl.create_default_context()
            url = f"https://v2.jokeapi.dev/joke/{category}?safe-mode"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'AIAssistant/6.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            if data.get("type") == "twopart":
                return {
                    "success": True,
                    "joke": f"{data.get('setup', '')} ... {data.get('delivery', '')}",
                    "category": data.get("category", "")
                }
            else:
                return {
                    "success": True,
                    "joke": data.get("joke", ""),
                    "category": data.get("category", "")
                }
        except:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "Why did the developer go broke? Because he used up all his cache!",
                "What do you call a fake noodle? An impasta!",
                "Why did the AI go to school? To get a little more byte!",
            ]
            return {"success": True, "joke": random.choice(jokes), "category": "demo"}


# ==================== CORE AI CLASSES ====================

class Memory:
    def __init__(self, content: str, importance: float = 0.5, emotion: str = "neutral"):
        self.content = content
        self.importance = importance
        self.emotion = emotion
        self.timestamp = datetime.now()
        self.access_count = 0

    def to_dict(self) -> Dict:
        return {"content": self.content, "importance": self.importance, "emotion": self.emotion, 
                "timestamp": self.timestamp.isoformat(), "access_count": self.access_count}


class EmotionDetector:
    POSITIVE = {"happy", "joy", "love", "great", "wonderful", "amazing", "excellent", "fantastic", "good", 
                "awesome", "beautiful", "perfect", "excited", "glad", "pleased", "thank", "thanks", "appreciate", "like", "love"}
    NEGATIVE = {"sad", "angry", "hate", "terrible", "awful", "bad", "horrible", "worst", "disappointed", 
                "frustrated", "upset", "annoyed", "mad", "cry", "unfortunately", "sorry", "problem", "issue", "fail"}

    @classmethod
    def detect_emotion(cls, text: str) -> str:
        text_lower = text.lower()
        words = set(text_lower.split())
        pos = len(words & cls.POSITIVE)
        neg = len(words & cls.NEGATIVE)
        if pos > neg: return "happy"
        elif neg > pos: return "sad"
        return "neutral"

    @classmethod
    def get_sentiment(cls, text: str) -> float:
        text_lower = text.lower()
        words = set(text_lower.split())
        pos = len(words & cls.POSITIVE)
        neg = len(words & cls.NEGATIVE)
        if pos + neg == 0: return 0.0
        return (pos - neg) / (pos + neg)


class DataStore:
    def __init__(self):
        self.collections: Dict[str, List[Dict]] = defaultdict(list)

    def insert(self, collection: str, data: Dict) -> str:
        record_id = hashlib.md5(f"{collection}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        record = {"_id": record_id, **data, "_created": datetime.now().isoformat()}
        self.collections[collection].append(record)
        return record_id

    def find(self, collection: str, query: Optional[Dict] = None) -> List[Dict]:
        if collection not in self.collections: return []
        if not query: return self.collections[collection]
        return [r for r in self.collections[collection] if all(r.get(k) == v for k, v in query.items())]

    def count(self, collection: str) -> int: return len(self.collections.get(collection, []))
    def list_collections(self) -> List[str]: return list(self.collections.keys())


class NeuralNetwork:
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        self.input_size, self.hidden_size, self.output_size = input_size, hidden_size, output_size
        self.weights_input = [[random.uniform(-1, 1) for _ in range(hidden_size)] for _ in range(input_size)]
        self.weights_output = [[random.uniform(-1, 1) for _ in range(output_size)] for _ in range(hidden_size)]
        self.bias_hidden, self.bias_output = [0.0] * hidden_size, [0.0] * output_size

    def _sigmoid(self, x: float) -> float: return 1 / (1 + math.exp(-max(min(x, 500), -500)))
    def _dot(self, a: List, b: List) -> float: return sum(x * y for x, y in zip(a, b))

    def predict(self, inputs: List[float]) -> List[float]:
        hidden = [self._sigmoid(self._dot(inputs, self.weights_input[i]) + self.bias_hidden[i]) for i in range(self.hidden_size)]
        return [self._sigmoid(self._dot(hidden, self.weights_output[i]) + self.bias_output[i]) for i in range(self.output_size)]

    def train(self, inputs: List[float], targets: List[float], epochs: int = 100):
        for _ in range(epochs):
            hidden = [self._sigmoid(self._dot(inputs, self.weights_input[i]) + self.bias_hidden[i]) for i in range(self.hidden_size)]
            outputs = [self._sigmoid(self._dot(hidden, self.weights_output[i]) + self.bias_output[i]) for i in range(self.output_size)]
            output_errors = [targets[i] - outputs[i] for i in range(self.output_size)]
            for i in range(self.output_size):
                for j in range(self.hidden_size):
                    self.weights_output[j][i] += 0.1 * output_errors[i] * hidden[j]


class LanguageEngine:
    TRANSLATIONS = {
        "es": {"hello": "hola", "goodbye": "adiós", "thank you": "gracias", "yes": "sí", "no": "no"},
        "fr": {"hello": "bonjour", "goodbye": "au revoir", "thank you": "merci", "yes": "oui", "no": "non"},
        "de": {"hello": "hallo", "goodbye": "auf wiedersehen", "thank you": "danke", "yes": "ja", "no": "nein"},
        "it": {"hello": "ciao", "goodbye": "arrivederci", "thank you": "grazie", "yes": "sì", "no": "no"},
        "ja": {"hello": "こんにちは", "goodbye": "さようなら", "thank you": "ありがとう"},
        "zh": {"hello": "你好", "goodbye": "再见", "thank you": "谢谢"},
        "ko": {"hello": "안녕하세요", "goodbye": "안녕히 가세요", "thank you": "감사합니다"},
    }
    LANG_NAMES = {"es": "Spanish", "fr": "French", "de": "German", "it": "Italian", 
                  "ja": "Japanese", "zh": "Chinese", "ko": "Korean", "en": "English"}

    @classmethod
    def translate(cls, text: str, target: str) -> str:
        text_lower = text.lower().strip()
        if target in cls.TRANSLATIONS and text_lower in cls.TRANSLATIONS[target]:
            return cls.TRANSLATIONS[target][text_lower]
        return f"[{target.upper()}] {text}"

    @classmethod
    def detect(cls, text: str) -> str:
        text_lower = text.lower()
        indicators = {"es": ["hola", "gracias"], "fr": ["bonjour", "merci"], "de": ["danke", "hallo"], 
                      "ja": ["こんにちは"], "zh": ["你好"], "ko": ["안녕하세요"]}
        for lang, words in indicators.items():
            if any(w in text_lower for w in words): return lang
        return "en"


class AI:
    def __init__(self):
        self.name = "Assistant"
        self.version = "6.0"
        self.memory: List[Memory] = []
        self.knowledge: Dict[str, Any] = {}
        self.db = DataStore()
        self.nn: Optional[NeuralNetwork] = None
        self.conversation_count = 0
        
        # API connections
        self.api_config = APIConfig()
        self.weather_api = WeatherAPI(self.api_config.get("openweather"))
        self.news_api = NewsAPI(self.api_config.get("newsapi"))
        
    def chat(self, user_input: str) -> str:
        self.conversation_count += 1
        text = user_input.lower().strip()
        
        # Greetings
        if text in ["hello", "hi", "hey", "greetings"]:
            return f"Hello! I'm your AI Assistant with real API connections!\n\nI can access live data from:\n• Wikipedia (search & definitions)\n• Weather (real data with API key)\n• News (live headlines with API key)\n• Dictionary (free, no key needed)\n• Jokes (free!)\n\nTry: 'wiki python', 'weather London', 'news', 'define love', 'joke'"
        
        if text in ["help", "commands", "what can you do", "help me"]:
            return """I can help with:

🔍 WIKIPEDIA (FREE):
• wiki python - Search Wikipedia
• wikipedia artificial intelligence - Get summary

🌤️ WEATHER:
• weather London - Current weather
• forecast Paris - 5-day forecast
(Add API key for real data)

📰 NEWS:
• news - Top headlines
• news technology - Tech news
(Add API key for real data)

📖 DICTIONARY (FREE):
• define happiness - Word definition

😂 JOKES (FREE):
• joke - Random joke
• joke programming - Programming joke

🔢 MATH:
• calculate 2+2*3
• random 1 100

🌍 TRANSLATION:
• translate hello to es
• detect language hola

🗄️ DATABASE:
• db insert {"name":"John"}
• db list

🧠 ML:
• init nn 3 5 2
• train nn [1,0] with [1]
• predict [1,0,1]

🔐 CRYPTO:
• md5 password
• uuid

💻 CODE:
• python print('Hello')

📊 AND MORE:
• sentiment analysis, unit conversion, etc."""
        
        # Wikipedia search
        if text.startswith("wiki ") or text.startswith("wikipedia ") or text.startswith("search "):
            query = user_input.replace("wiki ", "").replace("wikipedia ", "").replace("search ", "")
            result = WikipediaAPI.search(query)
            if result.get("success"):
                output = f"🔍 Wikipedia results for '{query}':\n\n"
                for i, r in enumerate(result.get("results", [])[:5], 1):
                    output += f"{i}. {r['title']}\n   {r['description'][:100]}...\n\n"
                return output
            return f"Wikipedia search failed: {result.get('error', 'Unknown error')}"
        
        # Wikipedia summary
        if text.startswith("what is ") or text.startswith("who is ") or text.startswith("tell me about "):
            topic = user_input.replace("what is ", "").replace("who is ", "").replace("tell me about ", "")
            result = WikipediaAPI.get_summary(topic)
            if result.get("success"):
                return f"📖 {result['title']}\n\n{result['description']}\n🔗 {result.get('url', '')}"
            return f"Could not find information about '{topic}'"
        
        # Dictionary
        if text.startswith("define ") or text.startswith("dictionary "):
            word = user_input.replace("define ", "").replace("dictionary ", "")
            result = DictionaryAPI.lookup(word)
            if result.get("success"):
                output = f"📖 Definition of '{result['word']}' {result.get('phonetic', '')}\n\n"
                for meaning in result.get("meanings", [])[:3]:
                    output += f"({meaning['part_of_speech']}) {meaning['definition']}\n\n"
                return output
            return f"Could not find definition for '{word}'"
        
        # Jokes
        if "joke" in text:
            category = "Programming" if "programming" in text or "code" in text else "Any"
            result = JokeAPI.get_joke(category.lower())
            return f"😂 {result.get('joke', 'No joke found')}"
        
        # News
        if text in ["news", "headlines", "latest news"]:
            result = self.news_api.get_top_headlines()
            if result.get("success"):
                output = f"📰 Latest News:\n\n"
                for i, article in enumerate(result.get("articles", [])[:5], 1):
                    output += f"{i}. {article['title']}\n   Source: {article['source']}\n\n"
                return output
            return "Could not fetch news"
        
        if text.startswith("news "):
            topic = user_input[5:]
            result = self.news_api.search_news(topic)
            if result.get("success"):
                output = f"📰 News about '{topic}':\n\n"
                for i, article in enumerate(result.get("articles", [])[:5], 1):
                    output += f"{i}. {article['title']}\n   {article.get('description', '')[:80]}...\n\n"
                return output
            return "Could not search news"
        
        # Weather
        if text.startswith("weather ") or text.startswith("forecast "):
            city = text.split(maxsplit=1)[1] if " " in text else "Unknown"
            if "forecast" in text or "5 day" in text or "5-day" in text:
                result = self.weather_api.get_forecast(city)
                if result.get("success"):
                    output = f"🌤️ 5-Day Forecast for {city.title()}:\n\n"
                    for day in result.get("forecast", [])[:5]:
                        output += f"Day {day['day']}: {day['temp']}°C, {day['description']}\n"
                    return output
            else:
                result = self.weather_api.get_weather(city)
                if result.get("success"):
                    source = result.get("source", "real")
                    return f"🌤️ Weather in {result['city']}, {result['country']}:\n\nTemperature: {result['temp']}°C (feels like {result['feels_like']}°C)\nHumidity: {result['humidity']}%\nCondition: {result['description']}\n{'[Mock Data]' if source == 'mock' else '[Live Data]'}"
            return f"Could not get weather for {city}"
        
        # API Settings
        if text.startswith("apikey ") or text.startswith("set api "):
            parts = user_input.replace("apikey ", "").replace("set api ", "").split()
            if len(parts) >= 2:
                service = parts[0].lower()
                key = parts[1]
                if service in ["weather", "openweather"]:
                    self.api_config.set("openweather", key)
                    self.weather_api = WeatherAPI(key)
                    return "✅ Weather API key saved! Real weather data enabled."
                elif service in ["news", "newsapi"]:
                    self.api_config.set("newsapi", key)
                    self.news_api = NewsAPI(key)
                    return "✅ News API key saved! Real news data enabled."
            return "Usage: apikey weather YOUR_API_KEY\n\nGet free keys:\n- Weather: openweathermap.org\n- News: newsapi.org"
        
        if text in ["api status", "api keys"]:
            weather_key = "✓ Configured" if self.api_config.get("openweather") else "✗ Not set"
            news_key = "✓ Configured" if self.api_config.get("newsapi") else "✗ Not set"
            return f"""🔑 API Status:
──────────────
Weather API: {weather_key}
News API: {news_key}

To set keys: apikey weather YOUR_KEY"""
        
        # Math
        if text.startswith("calc ") or text.startswith("calculate "):
            expr = text.replace("calculate ", "").replace("calc ", "")
            try: return str(eval(expr, {"__builtins__": {}, "math": math}))
            except: return "Invalid calculation"
        
        if text.startswith("random "):
            parts = text.split()
            if len(parts) == 3:
                try: return str(random.randint(int(parts[1]), int(parts[2])))
                except: pass
            return str(random.randint(1, 100))
        
        if text == "time": return f"Current time: {datetime.now().strftime('%H:%M:%S')}"
        if text == "date": return f"Today's date: {datetime.now().strftime('%Y-%m-%d')}"
        
        # Translation
        if text.startswith("translate ") and " to " in text:
            parts = user_input[10:].split(" to ")
            if len(parts) == 2:
                return LanguageEngine.translate(parts[0].strip(), parts[1].strip())
        
        if text.startswith("detect language ") or text.startswith("lang "):
            lang = LanguageEngine.detect(user_input.split(maxsplit=1)[1])
            return f"Detected: {lang} ({LanguageEngine.LANG_NAMES.get(lang, 'Unknown')})"
        
        # Database
        if text.startswith("db insert ") or text.startswith("insert "):
            try:
                data = json.loads(user_input.split(maxsplit=1)[1])
                coll = data.pop("collection", "default")
                return f"Inserted: {self.db.insert(coll, data)}"
            except: return "Try: db insert {\"collection\":\"users\",\"name\":\"John\"}"
        
        if text in ["db list", "db collections", "list databases"]:
            colls = self.db.list_collections()
            return f"Collections: {', '.join(colls) if colls else 'None'}"
        
        if text.startswith("db count ") or text.startswith("count "):
            return f"Count: {self.db.count(text.split(maxsplit=1)[1])}"
        
        # Neural Network
        if text.startswith("init nn "):
            try:
                parts = [int(x) for x in text.split()[2:]]
                self.nn = NeuralNetwork(parts[0], parts[1], parts[2])
                return f"Neural network created: {parts[0]} input, {parts[1]} hidden, {parts[2]} output"
            except: return "Try: init nn 3 5 2"
        
        if text.startswith("train nn "):
            if not self.nn: return "Create network first: init nn 3 5 2"
            try:
                parts = user_input[9:].split(" with ")
                inputs = json.loads(parts[0])
                targets = json.loads(parts[1])
                self.nn.train(inputs, targets)
                return "Training complete!"
            except: return "Try: train nn [1,0,1] with [1,0]"
        
        if text.startswith("predict ") or text.startswith("nn predict "):
            if not self.nn: return "Create network first: init nn 3 5 2"
            try:
                inputs = json.loads(text.split(maxsplit=1)[1])
                result = self.nn.predict(inputs)
                return f"Prediction: {result}"
            except: return "Try: predict [1,0,1]"
        
        # Crypto
        if text.startswith("md5 ") or text.startswith("hash "):
            data = text.split(maxsplit=1)[1] if " " in text else ""
            return f"MD5: {hashlib.md5(data.encode()).hexdigest()}"
        
        if text.startswith("sha256 "):
            data = text[7:] if len(text) > 7 else ""
            return f"SHA256: {hashlib.sha256(data.encode()).hexdigest()}"
        
        if text in ["uuid", "generate uuid", "guid"]:
            return f"UUID: {str(uuid.uuid4())}"
        
        if text.startswith("base64 encode "):
            return base64.b64encode(user_input[13:].encode()).decode()
        
        if text.startswith("base64 decode "):
            try: return base64.b64decode(user_input[14:].encode()).decode()
            except: return "Invalid base64"
        
        # Unit conversion
        if text.startswith("convert ") and " to " in text:
            try:
                parts = text[8:].split(" to ")
                val, from_u, to_u = float(parts[0].split()[0]), parts[0].split()[1], parts[1]
                conversions = {"km_mi": 0.621371, "mi_km": 1.60934, "kg_lb": 2.20462, "lb_kg": 0.453592,
                             "c_f": lambda c: c*9/5+32, "f_c": lambda f: (f-32)*5/9, "m_ft": 3.28084, "ft_m": 0.3048}
                key = f"{from_u}_{to_u}"
                if key in conversions:
                    result = conversions[key](val) if callable(conversions[key]) else val * conversions[key]
                    return f"{val} {from_u} = {result:.2f} {to_u}"
            except: pass
        
        # Sentiment
        if text.startswith("sentiment ") or text.startswith("analyze "):
            analysis = EmotionDetector.get_sentiment(user_input.split(maxsplit=1)[1])
            sentiment = "positive" if analysis > 0.1 else "negative" if analysis < -0.1 else "neutral"
            return f"Sentiment: {sentiment} ({analysis:.2f})"
        
        # Currency (mock)
        if "currency" in text or ("convert " in text and ("usd" in text.lower() or "eur" in text.lower())):
            return f"Currency conversion: Using mock rates. Add API key for real data."
        
        # Code execution
        if text.startswith("python ") or text.startswith("run "):
            code = user_input.replace("python ", "").replace("run ", "")
            try:
                result = []
                exec(code, {"__builtins__": {"print": lambda x: result.append(str(x)), "len": len, "range": range, "str": str, "int": int, "list": list, "dict": dict, "math": math, "random": random}})
                return f"Executed. Output: {', '.join(result) if result else 'No output'}"
            except Exception as e: return f"Error: {str(e)}"
        
        # Stats
        if text in ["stats", "statistics", "about", "status"]:
            return f"""AI Assistant v{self.version}
==========================
Conversations: {self.conversation_count}
Memories stored: {len(self.memory)}
Knowledge topics: {len(self.knowledge)}
Database collections: {len(self.db.list_collections())}
Neural Network: {'Active' if self.nn else 'Not initialized'}
Weather API: {'Connected' if self.api_config.get('openweather') else 'Using mock data'}
News API: {'Connected' if self.api_config.get('newsapi') else 'Using mock data'}"""
        
        # Learn/Remember
        if "remember" in text or "learn" in text:
            self.memory.append(Memory(user_input, 0.5))
            if len(self.memory) > 50: self.memory = self.memory[-50:]
            return "Got it! I've stored that information."
        
        # Knowledge base
        if "what do you know" in text or "knowledge" in text:
            return f"I know about: {', '.join(self.knowledge.keys()) if self.knowledge else 'Nothing stored yet'}"
        
        if text.startswith("know ") or text.startswith("learn "):
            topic = text.split(maxsplit=1)[1].split(" is ")[0] if " is " in text else text.split(maxsplit=1)[1]
            value = text.split(" is ")[1] if " is " in text else "Information stored"
            self.knowledge[topic] = value
            return f"I'll remember that: {topic} = {value}"
        
        # Default response
        responses = [
            f"I understand: '{user_input}'. Try 'help' for all commands!",
            f"That's interesting! Say 'help' to see what I can do.",
            f"I heard you! Type 'help' for ideas.",
        ]
        return random.choice(responses)


# ==================== GUI APPLICATION ====================

class AIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant v6.0 - With Real APIs")
        self.root.geometry("950x750")
        self.root.minsize(750, 550)
        
        # Modern dark theme colors
        self.bg_color = "#1a1a2e"
        self.bg_light = "#16213e"
        self.accent = "#0f3460"
        self.primary = "#e94560"
        self.text = "#eaeaea"
        self.text_dim = "#a0a0a0"
        self.success = "#00d9a5"
        
        self.root.configure(bg=self.bg_color)
        self.ai = AI()
        self.is_processing = False
        
        self._setup_styles()
        self._create_header()
        self._create_notebook()
        self._create_input_area()
        self._create_status_bar()
        
        # Welcome message
        self.add_message("AI", f"Welcome to AI Assistant v6.0!\n\n🆕 NEW: Real API Connections!\n• Wikipedia - Search & summaries\n• Weather - Live data (needs API key)\n• News - Headlines (needs API key)\n• Dictionary - Free definitions\n• Jokes - Free & unlimited!\n\nTry these commands:\n• 'wiki python'\n• 'weather London'\n• 'news technology'\n• 'define happiness'\n• 'joke'\n• 'help' - See all commands", "welcome")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=self.bg_color)
        style.configure("TNotebook.Tab", background=self.bg_light, foreground=self.text, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", self.accent)], foreground=[("selected", self.success)])
        style.configure("TFrame", background=self.bg_color)

    def _create_header(self):
        header = tk.Frame(self.root, bg=self.bg_color)
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        # Logo/Icon
        icon_label = tk.Label(header, text="🤖", font=("Arial", 28), bg=self.bg_color)
        icon_label.pack(side="left")
        
        # Title
        title_frame = tk.Frame(header, bg=self.bg_color)
        title_frame.pack(side="left", padx=15)
        
        tk.Label(title_frame, text="AI Assistant v6.0", font=("Arial", 22, "bold"), bg=self.bg_color, fg=self.success).pack(anchor="w")
        tk.Label(title_frame, text="With Real API Connections", font=("Arial", 10), bg=self.bg_color, fg=self.text_dim).pack(anchor="w")
        
        # Quick action buttons
        btn_frame = tk.Frame(header, bg=self.bg_color)
        btn_frame.pack(side="right")
        
        self._create_button(btn_frame, "Help", self.show_help, "#3498db").pack(side="left", padx=3)
        self._create_button(btn_frame, "Clear", self.clear_chat, "#e74c3c").pack(side="left", padx=3)
        self._create_button(btn_frame, "Save", self.save_session, "#27ae60").pack(side="left", padx=3)
        self._create_button(btn_frame, "API Keys", self.show_api_settings, "#9b59b6").pack(side="left", padx=3)

    def _create_button(self, parent, text, command, color):
        return tk.Button(parent, text=text, command=command, bg=color, fg="white", 
                        font=("Arial", 9, "bold"), relief="flat", padx=12, pady=6, cursor="hand2")

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Chat Tab
        self.chat_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.chat_frame, text="💬 Chat")
        
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame, bg=self.bg_light, fg=self.text, font=("Consolas", 11),
            relief="flat", wrap="word", padx=15, pady=15
        )
        self.chat_display.pack(fill="both", expand=True)
        self.chat_display.tag_config("user", foreground="#3498db", spacing1=5)
        self.chat_display.tag_config("ai", foreground=self.success, spacing1=5)
        self.chat_display.tag_config("welcome", foreground="#f39c12", spacing1=10)
        self.chat_display.tag_config("error", foreground="#e74c3c")
        self.chat_display.tag_config("system", foreground=self.text_dim, font=("Consolas", 10))
        
        # Features Tab
        self.features_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.features_frame, text="📚 Features & APIs")
        self._create_features_tab()
        
        # API Tab
        self.api_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.api_frame, text="🔑 API Settings")
        self._create_api_tab()
        
        # About Tab
        self.about_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.about_frame, text="ℹ️ About")
        self._create_about_tab()

    def _create_features_tab(self):
        features = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                      AI ASSISTANT v6.0 - FEATURES                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  🌐 REAL API CONNECTIONS (v6.0)                                              ║
║  ────────────────────────────────                                             ║
║                                                                               ║
║  🔍 WIKIPEDIA (FREE - No key needed!)                                        ║
║  ─────────────────────────────────────                                       ║
║  • wiki python                    - Search Wikipedia                         ║
║  • what is machine learning      - Get summary                              ║
║                                                                               ║
║  📖 DICTIONARY (FREE - No key needed!)                                       ║
║  ─────────────────────────────────────                                       ║
║  • define happiness              - Word definition                          ║
║  • dictionary love              - Synonyms & meaning                       ║
║                                                                               ║
║  😂 JOKES (FREE - No key needed!)                                            ║
║  ───────────────────────────────────                                         ║
║  • joke                         - Random joke                              ║
║  • joke programming              - Programming joke                         ║
║                                                                               ║
║  🌤️ WEATHER (Needs API key - Free tier available)                           ║
║  ───────────────────────────────────────────────                             ║
║  • weather London               - Current weather                          ║
║  • forecast Paris               - 5-day forecast                           ║
║  • apikey weather YOUR_KEY      - Set API key                               ║
║                                                                               ║
║  📰 NEWS (Needs API key - Free tier available)                              ║
║  ─────────────────────────────────────────                                    ║
║  • news                         - Top headlines                            ║
║  • news technology              - Tech news                                 ║
║  • apikey news YOUR_KEY         - Set API key                               ║
║                                                                               ║
║  🔢 MATH & CALCULATIONS                                                      ║
║  ───────────────────────────────                                             ║
║  • calculate 2+2*3               - Basic math                               ║
║  • random 1 100                 - Random numbers                           ║
║  • convert 100 km to mi         - Unit conversions                         ║
║                                                                               ║
║  🌍 LANGUAGE                                                                  ║
║  ───────────────                                                             ║
║  • translate hello to es        - Translation                              ║
║  • detect language hola         - Detection                                ║
║                                                                               ║
║  🗄️ DATABASE                                                                ║
║  ───────────                                                                 ║
║  • db insert {\"name\":\"John\"}      - Insert data                             ║
║  • db list                       - List collections                         ║
║                                                                               ║
║  🧠 MACHINE LEARNING                                                         ║
║  ───────────────────                                                         ║
║  • init nn 3 5 2                - Create network                           ║
║  • train nn [1,0] with [1]      - Train                                    ║
║  • predict [1,0,1]              - Predict                                  ║
║                                                                               ║
║  🔐 CRYPTOGRAPHY                                                             ║
║  ───────────────                                                             ║
║  • md5 password                 - MD5 hash                                  ║
║  • uuid                         - Generate UUID                             ║
║                                                                               ║
║  💻 CODE EXECUTION                                                           ║
║  ─────────────────                                                           ║
║  • python print('Hello')       - Run Python                                ║
║                                                                               ║
║  📊 ANALYSIS                                                                 ║
║  ──────────                                                                  ║
║  • sentiment I love this        - Sentiment                                 ║
║  • stats                        - AI statistics                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        text = tk.Text(self.features_frame, bg=self.bg_color, fg=self.success, font=("Consolas", 9), relief="flat")
        text.pack(fill="both", expand=True, padx=20, pady=20)
        text.insert("1.0", features)
        text.config(state="disabled")

    def _create_api_tab(self):
        api_frame = tk.Frame(self.api_frame, bg=self.bg_color)
        api_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(api_frame, text="🔑 API Configuration", font=("Arial", 18, "bold"), bg=self.bg_color, fg=self.success).pack(pady=(0, 20))
        
        # Weather API
        tk.Label(api_frame, text="🌤️ Weather API (OpenWeatherMap)", font=("Arial", 12, "bold"), bg=self.bg_color, fg=self.text).pack(anchor="w", pady=(10, 5))
        tk.Label(api_frame, text="Get free key at: openweathermap.org", bg=self.bg_color, fg=self.text_dim, font=("Arial", 9)).pack(anchor="w")
        
        self.weather_key_entry = tk.Entry(api_frame, bg=self.bg_light, fg=self.text, font=("Arial", 11), width=50)
        self.weather_key_entry.pack(anchor="w", pady=5)
        self.weather_key_entry.insert(0, self.ai.api_config.get("openweather"))
        
        tk.Button(api_frame, text="Save Weather Key", command=self.save_weather_key, bg="#3498db", fg="white", relief="flat", padx=15, pady=5).pack(anchor="w", pady=(0, 20))
        
        # News API
        tk.Label(api_frame, text="📰 News API", font=("Arial", 12, "bold"), bg=self.bg_color, fg=self.text).pack(anchor="w", pady=(10, 5))
        tk.Label(api_frame, text="Get free key at: newsapi.org", bg=self.bg_color, fg=self.text_dim, font=("Arial", 9)).pack(anchor="w")
        
        self.news_key_entry = tk.Entry(api_frame, bg=self.bg_light, fg=self.text, font=("Arial", 11), width=50)
        self.news_key_entry.pack(anchor="w", pady=5)
        self.news_key_entry.insert(0, self.ai.api_config.get("newsapi"))
        
        tk.Button(api_frame, text="Save News Key", command=self.save_news_key, bg="#3498db", fg="white", relief="flat", padx=15, pady=5).pack(anchor="w", pady=(0, 20))
        
        # Status
        tk.Label(api_frame, text="📊 Current Status:", font=("Arial", 12, "bold"), bg=self.bg_color, fg=self.text).pack(anchor="w", pady=(20, 10))
        
        self.api_status_label = tk.Label(api_frame, text="", bg=self.bg_color, fg=self.text_dim, font=("Arial", 10), justify="left")
        self.api_status_label.pack(anchor="w")
        self.update_api_status()
        
        # Instructions
        tk.Label(api_frame, text="💡 Tip: Some features work without API keys!\n• Wikipedia search\n• Dictionary\n• Jokes", bg=self.bg_color, fg=self.text_dim, font=("Arial", 9), justify="left").pack(anchor="w", pady=(30, 0))

    def update_api_status(self):
        weather = "✓ Connected" if self.ai.api_config.get("openweather") else "✗ Using mock data"
        news = "✓ Connected" if self.ai.api_config.get("newsapi") else "✗ Using mock data"
        self.api_status_label.config(text=f"Weather API: {weather}\nNews API: {news}")

    def save_weather_key(self):
        key = self.weather_key_entry.get().strip()
        self.ai.api_config.set("openweather", key)
        self.ai.weather_api = WeatherAPI(key)
        self.update_api_status()
        messagebox.showinfo("Saved", "Weather API key saved!")

    def save_news_key(self):
        key = self.news_key_entry.get().strip()
        self.ai.api_config.set("newsapi", key)
        self.ai.news_api = NewsAPI(key)
        self.update_api_status()
        messagebox.showinfo("Saved", "News API key saved!")

    def _create_about_tab(self):
        about_frame = tk.Frame(self.about_frame, bg=self.bg_color)
        about_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(about_frame, text="🤖", font=("Arial", 60), bg=self.bg_color).pack(pady=20)
        tk.Label(about_frame, text="AI Assistant", font=("Arial", 28, "bold"), bg=self.bg_color, fg=self.success).pack()
        tk.Label(about_frame, text="Version 6.0 - API Edition", font=("Arial", 14), bg=self.bg_color, fg=self.text_dim).pack()
        
        tk.Label(about_frame, text="Your personal AI companion", font=("Arial", 12), bg=self.bg_color, fg=self.text).pack(pady=20)
        
        info_text = """
Built with Python & Tkinter

API Connections:
• Wikipedia - Free
• Dictionary - Free
• Jokes API - Free
• OpenWeatherMap - Needs API key
• NewsAPI - Needs API key

Features:
• 50+ AI-powered commands
• Real-time data (with API keys)
• Natural language processing
• Machine learning
• Database operations

License: Free to use
        """
        tk.Label(about_frame, text=info_text, font=("Arial", 10), bg=self.bg_color, fg=self.text_dim, justify="center").pack(pady=20)
        
        tk.Label(about_frame, text="© 2024 AI Assistant", font=("Arial", 9), bg=self.bg_color, fg="#666").pack(side="bottom", pady=20)

    def _create_input_area(self):
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.input_entry = tk.Entry(
            input_frame, bg=self.bg_light, fg=self.text, font=("Arial", 12),
            relief="flat", insertbackground=self.success
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", self.send_message)
        self.input_entry.bind("<KP_Enter>", self.send_message)
        
        send_btn = tk.Button(
            input_frame, text="Send", command=self.send_message,
            bg=self.primary, fg="white", font=("Arial", 11, "bold"),
            relief="flat", padx=25, pady=8, cursor="hand2"
        )
        send_btn.pack(side="right")

    def _create_status_bar(self):
        self.status_bar = tk.Label(
            self.root, text="Ready • Type 'help' for commands",
            bg=self.accent, fg=self.text, font=("Arial", 9), anchor="w", padx=10, pady=5
        )
        self.status_bar.pack(fill="x")

    def send_message(self, event=None):
        if self.is_processing:
            return
        
        user_input = self.input_entry.get().strip()
        if not user_input:
            return

        self.input_entry.delete(0, "end")
        self.add_message("You", user_input, "user")
        self.status_bar.config(text="Processing...")
        
        self.is_processing = True
        
        def process():
            try:
                response = self.ai.chat(user_input)
                self.root.after(0, lambda: self.add_message("AI", response, "ai"))
            except Exception as e:
                self.root.after(0, lambda: self.add_message("Error", str(e), "error"))
            finally:
                self.is_processing = False
                self.root.after(0, lambda: self.status_bar.config(text="Ready"))

        threading.Thread(target=process, daemon=True).start()

    def add_message(self, sender: str, message: str, tag: str):
        self.chat_display.config(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}\n\n", tag)
        self.chat_display.see("end")
        self.chat_display.config(state="disabled")

    def clear_chat(self):
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.config(state="disabled")
        self.status_bar.config(text="Chat cleared")

    def show_help(self):
        self.notebook.select(0)
        self.add_message("AI", "Check the Features & APIs tab for all commands!", "ai")

    def show_api_settings(self):
        self.notebook.select(2)
        self.update_api_status()

    def save_session(self):
        try:
            data = {
                "name": self.ai.name,
                "version": self.ai.version,
                "knowledge": self.ai.knowledge,
                "conversation_count": self.ai.conversation_count
            }
            with open("ai_session.json", "w") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Saved", "Session saved!")
            self.status_bar.config(text="Session saved")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save: {e}")


def main():
    root = tk.Tk()
    
    try:
        from ctypes import windll
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("AIAssistant6.0")
    except:
        pass
    
    app = AIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
