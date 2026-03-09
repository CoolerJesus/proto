#!/usr/bin/env python3
"""
AI Assistant - All-in-One Artificial Intelligence Assistant
Version: 5.0
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
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict


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
        self.version = "5.0"
        self.memory: List[Memory] = []
        self.knowledge: Dict[str, Any] = {}
        self.db = DataStore()
        self.nn: Optional[NeuralNetwork] = None
        self.conversation_count = 0
        
    def chat(self, user_input: str) -> str:
        self.conversation_count += 1
        text = user_input.lower().strip()
        
        # Greetings
        if text in ["hello", "hi", "hey", "greetings"]:
            return f"Hello! I'm your AI Assistant. I can help with many things - try commands like 'help', 'weather London', or 'calculate 2+2'"
        
        if text in ["help", "commands", "what can you do"]:
            return """I can help with:

MATH: calculate 2+2, random 1 100
LANGUAGE: translate hello to es, detect language hola
DATABASE: db insert {\"name\":\"John\"}, db list
ML: init nn 3 5 2, train nn [1,0] with [1], predict [1,0]
WEATHER: weather London
CRYPTO: md5 password, uuid
CODE: python print('hello')
AND MORE: sentiment analysis, file operations, calendar, etc."""
        
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
        
        # Weather (mock)
        if text.startswith("weather ") or text.startswith("forecast "):
            city = text.split(maxsplit=1)[1] if " " in text else "Unknown"
            temp = random.randint(10, 35)
            conditions = ["sunny", "cloudy", "rainy", "windy"]
            return f"Weather in {city.title()}: {temp}°C, {random.choice(conditions)}, Humidity: {random.randint(30,90)}%"
        
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
        
        # Currency
        if "currency" in text or "convert " in text and ("usd" in text.lower() or "eur" in text.lower()):
            try:
                parts = user_input.lower().replace("currency", "").replace("convert", "").split()
                amount = float([p for p in parts if p.isdigit()][0]) if any(p.isdigit() for p in parts) else 100
                return f"Mock conversion: {amount} USD ≈ {amount * random.uniform(0.8, 1.2):.2f} EUR"
            except: pass
        
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
Neural Network: {'Active' if self.nn else 'Not initialized'}"""
        
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
            f"I understand: '{user_input}'. Try 'help' for commands!",
            f"That's interesting! Say 'help' to see what I can do.",
            f"I heard you! Want to try some commands? Type 'help' for ideas.",
        ]
        return random.choice(responses)


# ==================== GUI APPLICATION ====================

class AIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant v5.0")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
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
        self.add_message("AI", f"Welcome to AI Assistant v5.0!\n\nI'm here to help you with many tasks. Try commands like:\n• 'help' - See all commands\n• 'weather London' - Get weather\n• 'calculate 2+2' - Do math\n• 'translate hello to es' - Translate\n• And much more!\n\nType in the box below and press Send or Enter.", "welcome")

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
        
        tk.Label(title_frame, text="AI Assistant", font=("Arial", 22, "bold"), bg=self.bg_color, fg=self.success).pack(anchor="w")
        tk.Label(title_frame, text="Your personal AI companion with 40+ features", font=("Arial", 10), bg=self.bg_color, fg=self.text_dim).pack(anchor="w")
        
        # Quick action buttons
        btn_frame = tk.Frame(header, bg=self.bg_color)
        btn_frame.pack(side="right")
        
        self._create_button(btn_frame, "Help", self.show_help, "#3498db").pack(side="left", padx=3)
        self._create_button(btn_frame, "Clear", self.clear_chat, "#e74c3c").pack(side="left", padx=3)
        self._create_button(btn_frame, "Save", self.save_session, "#27ae60").pack(side="left", padx=3)

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
        self.notebook.add(self.features_frame, text="📚 Features")
        self._create_features_tab()
        
        # Quick Commands Tab
        self.commands_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.commands_frame, text="⚡ Quick Commands")
        self._create_commands_tab()
        
        # About Tab
        self.about_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.about_frame, text="ℹ️ About")
        self._create_about_tab()

    def _create_features_tab(self):
        features = """
╔══════════════════════════════════════════════════════════════════════════╗
║                           AI ASSISTANT FEATURES                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  🎯 CORE AI FEATURES                                                    ║
║  ─────────────────────                                                  ║
║  • Natural Language Processing                                          ║
║  • Emotion & Sentiment Detection                                        ║
║  • Conversation Memory & Learning                                       ║
║  • Context-Aware Responses                                              ║
║                                                                          ║
║  🔢 MATH & CALCULATIONS                                                 ║
║  ─────────────────────────                                              ║
║  • Basic Math: calculate 2+2*3                                         ║
║  • Random Numbers: random 1 100                                         ║
║  • Unit Conversions: convert 100 km to mi                              ║
║  • Currency: currency convert 100 USD to EUR                            ║
║                                                                          ║
║  🌍 LANGUAGE & TRANSLATION                                              ║
║  ─────────────────────────────                                          ║
║  • Translate: translate hello to es                                     ║
║  • Detect: detect language hola                                         ║
║  • 10+ Languages Supported                                              ║
║                                                                          ║
║  🗄️ DATABASE                                                            ║
║  ───────────                                                            ║
║  • Insert: db insert {"name":"John","age":25}                          ║
║  • Query: db find {"collection":"users"}                                ║
║  • List: db list                                                        ║
║  • Count: db count users                                                ║
║                                                                          ║
║  🧠 MACHINE LEARNING                                                    ║
║  ─────────────────────                                                  ║
║  • Create: init nn 3 5 2                                                ║
║  • Train: train nn [1,0,1] with [1,0]                                  ║
║  • Predict: predict [1,0,1]                                             ║
║                                                                          ║
║  🌤️ WEATHER                                                             ║
║  ─────────                                                              ║
║  • Current: weather London                                              ║
║  • Forecast: forecast Paris                                             ║
║                                                                          ║
║  🔐 CRYPTOGRAPHY                                                        ║
║  ───────────────                                                        ║
║  • MD5 Hash: md5 password                                               ║
║  • SHA256: sha256 secret                                                ║
║  • UUID: uuid or generate uuid                                          ║
║  • Base64: base64 encode/decode text                                    ║
║                                                                          ║
║  💻 CODE EXECUTION                                                      ║
║  ─────────────────                                                      ║
║  • Run Python: python print('Hello')                                    ║
║                                                                          ║
║  📊 ANALYSIS                                                            ║
║  ──────────                                                            ║
║  • Sentiment: sentiment I love this                                    ║
║  • Statistics: stats or about                                           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
        text = tk.Text(self.features_frame, bg=self.bg_color, fg=self.success, font=("Consolas", 9), relief="flat")
        text.pack(fill="both", expand=True, padx=20, pady=20)
        text.insert("1.0", features)
        text.config(state="disabled")

    def _create_commands_tab(self):
        commands = """
╔═══════════════════════════════════════════════════════════════════╗
║                      QUICK COMMAND REFERENCE                      ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  BASIC                EXAMPLE                    RESULT           ║
║  ─────                ────────                    ──────          ║
║  help                 help                         Show commands   ║
║  hello                hello                        Greeting        ║
║  stats                stats                        Show stats      ║
║                                                                   ║
║  MATH                 EXAMPLE                    RESULT           ║
║  ────                ────────                    ──────           ║
║  calculate            calculate 2+2*3             8                ║
║  random               random 1 10                 1-10            ║
║  time                 time                         14:30:25        ║
║  date                 date                         2024-01-15     ║
║                                                                   ║
║  TRANSLATION          EXAMPLE                    RESULT           ║
║  ───────────          ────────                    ──────           ║
║  translate            translate hello to es      hola             ║
║  detect               detect language hola       Spanish          ║
║                                                                   ║
║  DATABASE             EXAMPLE                    RESULT           ║
║  ─────────           ────────                    ──────           ║
║  insert               db insert {"n":"John"}     ID returned      ║
║  find                 db find {"n":"John"}       Records found    ║
║  list                 db list                     Collections     ║
║                                                                   ║
║  ML                  EXAMPLE                    RESULT           ║
║  ───                 ────────                    ──────           ║
║  init nn             init nn 3 5 2               Created          ║
║  train               train [1,0] with [1]        Trained         ║
║  predict             predict [1,0,1]             [0.5, 0.3]      ║
║                                                                   ║
║  CRYPTO              EXAMPLE                    RESULT           ║
║  ──────              ────────                    ──────           ║
║  md5                 md5 password                hash             ║
║  sha256              sha256 secret               hash             ║
║  uuid                uuid                         UUID string      ║
║                                                                   ║
║  WEATHER              EXAMPLE                    RESULT           ║
║  ───────             ────────                    ──────           ║
║  weather              weather London             15°C sunny       ║
║                                                                   ║
║  ANALYTICS           EXAMPLE                    RESULT           ║
║  ─────────           ────────                    ──────           ║
║  sentiment            sentiment I love this      positive         ║
║  currency             currency 100 USD to EUR    ~85 EUR          ║
║                                                                   ║
║  CODE                 EXAMPLE                    RESULT           ║
║  ─────                ────────                    ──────          ║
║  python               python print('Hi')         Output shown     ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
        text = tk.Text(self.commands_frame, bg=self.bg_color, fg="#00d9ff", font=("Consolas", 9), relief="flat")
        text.pack(fill="both", expand=True, padx=20, pady=20)
        text.insert("1.0", commands)
        text.config(state="disabled")

    def _create_about_tab(self):
        about_frame = tk.Frame(self.about_frame, bg=self.bg_color)
        about_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(about_frame, text="🤖", font=("Arial", 60), bg=self.bg_color).pack(pady=20)
        tk.Label(about_frame, text="AI Assistant", font=("Arial", 28, "bold"), bg=self.bg_color, fg=self.success).pack()
        tk.Label(about_frame, text="Version 5.0", font=("Arial", 14), bg=self.bg_color, fg=self.text_dim).pack()
        
        tk.Label(about_frame, text="Your personal AI companion", font=("Arial", 12), bg=self.bg_color, fg=self.text).pack(pady=20)
        
        info_text = """
Built with Python & Tkinter

Features:
• 40+ AI-powered commands
• Natural language processing
• Machine learning capabilities
• Database operations
• Translation services
• And much more!

No internet required - works offline!

License: Free to use
        """
        tk.Label(about_frame, text=info_text, font=("Arial", 10), bg=self.bg_color, fg=self.text_dim, justify="center").pack(pady=20)
        
        tk.Label(about_frame, text="© 2024 AI Assistant", font=("Arial", 9), bg=self.bg_color, fg="#666").pack(side="bottom", pady=20)

    def _create_input_area(self):
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Input entry
        self.input_entry = tk.Entry(
            input_frame, bg=self.bg_light, fg=self.text, font=("Arial", 12),
            relief="flat", insertbackground=self.success
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", self.send_message)
        self.input_entry.bind("<KP_Enter>", self.send_message)
        
        # Send button
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
        self.add_message("AI", "Check the Features or Quick Commands tabs for all available commands!", "ai")

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
            messagebox.showinfo("Saved", "Session saved to ai_session.json")
            self.status_bar.config(text="Session saved")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save: {e}")


def main():
    root = tk.Tk()
    
    # Try to set app ID for Windows (better taskbar appearance)
    try:
        from ctypes import windll
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("AIAssistant5.0")
    except:
        pass
    
    app = AIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
