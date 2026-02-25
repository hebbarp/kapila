# -*- coding: utf-8 -*-
"""
Kapila NL Engine — Natural Language to Kapila Code
===================================================
Uses PicoNN (from D:/atrimed/sales) for intent classification
and Pampa (from D:/pampa) for akshara-aware text processing.

Architecture:
  Kannada sentence → keyword features → PicoNN MLP → intent
  intent + extracted params → Kapila code template → executable code
"""

import sys
import os
import re
import random

# Add dependency paths (local dev overrides; on server these are in the app dir)
if os.path.isdir("D:/atrimed/sales"):
    sys.path.insert(0, "D:/atrimed/sales")
if os.path.isdir("D:/pampa"):
    sys.path.insert(0, "D:/pampa")

from piconn import Value, MLP, Adam, cross_entropy_loss, softmax
from core import split_aksharas

# ---------------------------------------------------------------------------
# Intent definitions
# ---------------------------------------------------------------------------
INTENTS = ["add", "subtract", "multiply", "divide", "square", "hello", "print_num", "list_ops"]
INTENT_TO_IDX = {name: i for i, name in enumerate(INTENTS)}

# ---------------------------------------------------------------------------
# Keyword features — presence of these words/stems in input
#
# Each keyword is a signal. The MLP learns which combination → which intent.
# Grouped by the intent they most strongly indicate:
# ---------------------------------------------------------------------------
KEYWORDS = [
    # add signals (0-4)
    "ಕೂಡು", "ಕೂಡಿಸು", "ಜೋಡಿಸು", "ಮೊತ್ತ", "ಒಟ್ಟು",
    # subtract signals (5-9)
    "ಕಳೆ", "ಕಳೆಯ", "ವ್ಯವಕಲನ", "ಕಡಿಮೆ", "ಬಿಟ್ಟು",
    # multiply signals (10-14)
    "ಗುಣಿಸು", "ಗುಣಾಕಾರ", "ಗುಣಿ", "ಗುಣಿಸಿ", "ಪಟ್ಟು",
    # divide signals (15-18)
    "ಭಾಗಿಸು", "ಭಾಗಾಕಾರ", "ಭಾಗ", "ಭಾಗಿಸಿ",
    # square signals (19-21)
    "ವರ್ಗ", "ಸ್ಕ್ವೇರ್", "ವರ್ಗಮೂಲ",
    # hello signals (22-25)
    "ನಮಸ್ಕಾರ", "ಹಲೋ", "ಹೆಲ್ಲೊ", "ಜಗತ್ತು",
    # print signals (26-28)
    "ಮುದ್ರಿಸು", "ತೋರಿಸು", "ಪ್ರಿಂಟ್",
    # list signals (29-31)
    "ಪಟ್ಟಿ", "ಉದ್ದ", "ಅಂಶ",
    # context words — NOT intent-specific, but help disambiguate (32-37)
    "ಮತ್ತು", "ಸಂಖ್ಯೆ", "ರೇಖೆ", "ಎಷ್ಟು", "ಮಾಡು", "ಫಲಿತಾಂಶ",
]

# ---------------------------------------------------------------------------
# Number extraction
# ---------------------------------------------------------------------------

# Kannada digit characters → int
KANNADA_DIGITS = {"೦": 0, "೧": 1, "೨": 2, "೩": 3, "೪": 4,
                  "೫": 5, "೬": 6, "೭": 7, "೮": 8, "೯": 9}

# Int → Kannada digit string
INT_TO_KANNADA = {v: k for k, v in KANNADA_DIGITS.items()}

# Kannada cardinal number words → value
KANNADA_NUM_WORDS = {
    "ಒಂದು": 1, "ಎರಡು": 2, "ಮೂರು": 3, "ನಾಲ್ಕು": 4, "ಐದು": 5,
    "ಆರು": 6, "ಏಳು": 7, "ಎಂಟು": 8, "ಒಂಬತ್ತು": 9, "ಹತ್ತು": 10,
    "ಹನ್ನೊಂದು": 11, "ಹನ್ನೆರಡು": 12, "ಹದಿಮೂರು": 13, "ಹದಿನಾಲ್ಕು": 14,
    "ಹದಿನೈದು": 15, "ಹದಿನಾರು": 16, "ಹದಿನೇಳು": 17, "ಹದಿನೆಂಟು": 18,
    "ಹತ್ತೊಂಬತ್ತು": 19,
    "ಇಪ್ಪತ್ತು": 20, "ಮೂವತ್ತು": 30, "ನಲವತ್ತು": 40, "ಐವತ್ತು": 50,
    "ಅರವತ್ತು": 60, "ಎಪ್ಪತ್ತು": 70, "ಎಂಬತ್ತು": 80, "ತೊಂಬತ್ತು": 90,
    "ನೂರು": 100, "ಸಾವಿರ": 1000,
}

# Kannada ordinal words → value (ಮೊದಲ=first, ಎರಡನೇ=second, etc.)
KANNADA_ORDINALS = {
    "ಮೊದಲ": 1, "ಮೊದಲನೇ": 1, "ಒಂದನೇ": 1,
    "ಎರಡನೇ": 2, "ಎರಡನೆಯ": 2,
    "ಮೂರನೇ": 3, "ಮೂರನೆಯ": 3,
    "ನಾಲ್ಕನೇ": 4, "ನಾಲ್ಕನೆಯ": 4,
    "ಐದನೇ": 5, "ಐದನೆಯ": 5,
    "ಆರನೇ": 6, "ಆರನೆಯ": 6,
    "ಏಳನೇ": 7, "ಏಳನೆಯ": 7,
    "ಎಂಟನೇ": 8, "ಎಂಟನೆಯ": 8,
    "ಒಂಬತ್ತನೇ": 9, "ಒಂಬತ್ತನೆಯ": 9,
    "ಹತ್ತನೇ": 10, "ಹತ್ತನೆಯ": 10,
    "ಹನ್ನೊಂದನೇ": 11, "ಹನ್ನೊಂದನೆಯ": 11,
    "ಹನ್ನೆರಡನೇ": 12, "ಹನ್ನೆರಡನೆಯ": 12,
    "ಹದಿಮೂರನೇ": 13, "ಹದಿನಾಲ್ಕನೇ": 14,
    "ಹದಿನೈದನೇ": 15, "ಹದಿನಾರನೇ": 16,
    "ಹದಿನೇಳನೇ": 17, "ಹದಿನೆಂಟನೇ": 18,
    "ಹತ್ತೊಂಬತ್ತನೇ": 19, "ಇಪ್ಪತ್ತನೇ": 20,
    "ನೂರನೇ": 100, "ಸಾವಿರದ": 1000,
}


def to_kannada_num(n):
    """Convert an integer to Kannada digit string."""
    s = str(int(n))
    return "".join(INT_TO_KANNADA.get(int(ch), ch) for ch in s)


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------
def extract_features(text: str) -> list:
    """Extract keyword-presence feature vector from Kannada text."""
    text = text.strip()
    features = []
    for kw in KEYWORDS:
        features.append(1.0 if kw in text else 0.0)
    return features


def extract_numbers(text: str) -> list:
    """Extract numbers from text in order of appearance."""
    found = []  # list of (position, value)
    covered = set()  # character positions already matched

    # 1. Kannada digit sequences (೧೨೩ → 123)
    kn_digit_pattern = "[" + "".join(KANNADA_DIGITS.keys()) + "]+"
    for match in re.finditer(kn_digit_pattern, text):
        val = int("".join(str(KANNADA_DIGITS[ch]) for ch in match.group()))
        found.append((match.start(), val))
        covered.update(range(match.start(), match.end()))

    # 2. ASCII digit sequences (only 0-9, skip positions already covered)
    for match in re.finditer(r"[0-9]+", text):
        if match.start() not in covered:
            found.append((match.start(), int(match.group())))
            covered.update(range(match.start(), match.end()))

    # 3. Ordinal words — check longest matches first to avoid partial matches
    for word, val in sorted(KANNADA_ORDINALS.items(), key=lambda x: -len(x[0])):
        idx = text.find(word)
        if idx >= 0 and not any(i in covered for i in range(idx, idx + len(word))):
            found.append((idx, val))
            covered.update(range(idx, idx + len(word)))

    # 4. Cardinal number words — longest first, skip overlaps
    for word, val in sorted(KANNADA_NUM_WORDS.items(), key=lambda x: -len(x[0])):
        idx = text.find(word)
        if idx >= 0 and not any(i in covered for i in range(idx, idx + len(word))):
            found.append((idx, val))
            covered.update(range(idx, idx + len(word)))

    # Sort by position in text and return values only
    found.sort(key=lambda x: x[0])
    return [val for _, val in found]


# ---------------------------------------------------------------------------
# Training data — (Kannada sentence, intent_name)
#
# Key principle: every intent needs examples WITH "ಮತ್ತು" and other shared
# context words so the MLP learns to disambiguate by operation keyword,
# not just by surrounding words.
# ---------------------------------------------------------------------------
TRAINING_DATA = [
    # --- add ---
    ("ಐದು ಮತ್ತು ಮೂರು ಕೂಡಿಸು", "add"),
    ("೫ ಮತ್ತು ೩ ಕೂಡು", "add"),
    ("ಎರಡು ಸಂಖ್ಯೆ ಕೂಡು", "add"),
    ("೧೦ ೨೦ ಕೂಡಿಸು", "add"),
    ("ಮೊತ್ತ ಕಂಡುಹಿಡಿ", "add"),
    ("ಜೋಡಿಸು ೭ ೮", "add"),
    ("೩ ೪ ಕೂಡು", "add"),
    ("ನಾಲ್ಕು ಆರು ಕೂಡಿಸು", "add"),
    ("೧೫ ಮತ್ತು ೨೫ ಕೂಡು", "add"),
    ("ಮೂರು ಏಳು ಜೋಡಿಸು", "add"),
    ("೨ + ೩", "add"),
    ("ಮೊದಲ ಮತ್ತು ಎರಡನೇ ಸಂಖ್ಯೆಗಳನ್ನು ಕೂಡು", "add"),
    ("ಸಂಖ್ಯಾ ರೇಖೆಯ ೫ ಮತ್ತು ೩ ಕೂಡಿಸು", "add"),
    ("ಒಟ್ಟು ೧೦ ೨೦", "add"),
    ("ಎರಡು ಸಂಖ್ಯೆಗಳನ್ನು ಕೂಡಿಸು ೫ ೩", "add"),
    ("೮ ಮತ್ತು ೭ ಕೂಡಿಸು", "add"),
    ("ಐದನೇ ಮತ್ತು ಮೂರನೇ ಸಂಖ್ಯೆ ಕೂಡು", "add"),
    ("ಒಂದು ಮತ್ತು ಒಂದು ಕೂಡಿಸು", "add"),

    # --- subtract ---
    ("೧೦ ರಿಂದ ೩ ಕಳೆ", "subtract"),
    ("ಹತ್ತು ಐದು ಕಳೆ", "subtract"),
    ("ವ್ಯವಕಲನ ೨೦ ೫", "subtract"),
    ("೧೫ ೭ ಕಳೆ", "subtract"),
    ("ಕಡಿಮೆ ಮಾಡು ೧೦ ೪", "subtract"),
    ("೧೦೦ ೫೦ ಕಳೆಯ", "subtract"),
    ("ಎಂಟು ಮೂರು ಕಳೆ", "subtract"),
    ("೯ ೫ ಕಳೆ", "subtract"),
    ("೨೦ - ೫", "subtract"),
    ("ಮೊದಲ ಸಂಖ್ಯೆಯಿಂದ ಎರಡನೇ ಸಂಖ್ಯೆ ಕಳೆ", "subtract"),
    ("೧೦ ಮತ್ತು ೩ ಕಳೆ", "subtract"),
    ("ಸಂಖ್ಯಾ ರೇಖೆಯ ೨೦ ಮತ್ತು ೫ ಕಳೆ", "subtract"),
    ("ಐದನೇ ಮತ್ತು ಮೂರನೇ ಸಂಖ್ಯೆಗಳನ್ನು ಕಳೆ", "subtract"),
    ("ಹನ್ನೆರಡು ಮತ್ತು ಐದು ಕಳೆ", "subtract"),
    ("ಬಿಟ್ಟು ೧೫ ೬", "subtract"),

    # --- multiply ---
    ("೬ ೭ ಗುಣಿಸು", "multiply"),
    ("ಆರು ಏಳು ಗುಣಿಸು", "multiply"),
    ("ಗುಣಾಕಾರ ೫ ೪", "multiply"),
    ("೩ ೮ ಗುಣಿಸು", "multiply"),
    ("೧೦ ೧೦ ಗುಣಿಸು", "multiply"),
    ("ಐದು ಐದು ಗುಣಿಸು", "multiply"),
    ("೯ ೩ ಗುಣಿಸು", "multiply"),
    ("೪ * ೫", "multiply"),
    ("ಮೊದಲ ಮತ್ತು ಎರಡನೇ ಸಂಖ್ಯೆಗಳನ್ನು ಗುಣಿಸು", "multiply"),
    ("ಸಂಖ್ಯಾ ರೇಖೆಯ ೫ ಮತ್ತು ೩ ಗುಣಿಸು", "multiply"),
    ("೧೦ ಮತ್ತು ೩ ಗುಣಿಸು", "multiply"),
    ("ಸಂಖ್ಯಾ ರೇಖೆಯ ಮೊದಲ ಮತ್ತು ಹನ್ನೆರಡನೇ ಸಂಖ್ಯೆಗಳನ್ನು ಗುಣಿಸು", "multiply"),
    ("ಐದನೇ ಮತ್ತು ಮೂರನೇ ಸಂಖ್ಯೆ ಗುಣಿಸು", "multiply"),
    ("ಹನ್ನೆರಡು ಮತ್ತು ಐದು ಗುಣಿಸು", "multiply"),
    ("ಎರಡು ಸಂಖ್ಯೆಗಳನ್ನು ಗುಣಿಸಿ", "multiply"),
    ("೬ ಪಟ್ಟು ೭", "multiply"),
    ("ಆರು ಮತ್ತು ಏಳು ಗುಣಿಸು", "multiply"),
    ("ಮೂರು ಮತ್ತು ಎಂಟು ಗುಣಿಸು", "multiply"),
    ("ಗುಣಿ ೫ ೭", "multiply"),

    # --- divide ---
    ("೧೦ ೨ ಭಾಗಿಸು", "divide"),
    ("ನೂರು ನಾಲ್ಕು ಭಾಗಿಸು", "divide"),
    ("ಭಾಗಾಕಾರ ೫೦ ೫", "divide"),
    ("೧೦೦ ೪ ಭಾಗಿಸು", "divide"),
    ("೨೦ ೫ ಭಾಗ ಮಾಡು", "divide"),
    ("ಹತ್ತು ಎರಡು ಭಾಗಿಸು", "divide"),
    ("೨೧ / ೩", "divide"),
    ("ಮೊದಲ ಸಂಖ್ಯೆಯನ್ನು ಎರಡನೇ ಸಂಖ್ಯೆಯಿಂದ ಭಾಗಿಸು", "divide"),
    ("೧೦೦ ಮತ್ತು ೪ ಭಾಗಿಸು", "divide"),
    ("ಸಂಖ್ಯಾ ರೇಖೆಯ ೨೦ ಮತ್ತು ೫ ಭಾಗಿಸು", "divide"),
    ("ಐದನೇ ಮತ್ತು ಮೂರನೇ ಸಂಖ್ಯೆ ಭಾಗಿಸು", "divide"),
    ("ಹನ್ನೆರಡು ಮತ್ತು ಮೂರು ಭಾಗಿಸು", "divide"),
    ("ಭಾಗಿಸಿ ೫೦ ೧೦", "divide"),

    # --- square ---
    ("ಐದರ ವರ್ಗ", "square"),
    ("೫ ವರ್ಗ", "square"),
    ("೭ ರ ವರ್ಗ ಎಷ್ಟು", "square"),
    ("ಮೂರು ವರ್ಗ", "square"),
    ("ವರ್ಗ ೧೦", "square"),
    ("೮ ವರ್ಗ ಮಾಡು", "square"),
    ("ಸ್ಕ್ವೇರ್ ೬", "square"),
    ("೯ ವರ್ಗ", "square"),
    ("ಹತ್ತು ವರ್ಗ", "square"),
    ("ಹನ್ನೆರಡು ವರ್ಗ", "square"),
    ("ಐದನೇ ಸಂಖ್ಯೆಯ ವರ್ಗ", "square"),
    ("೧೫ ವರ್ಗ ಎಷ್ಟು", "square"),
    ("ಸಂಖ್ಯೆಯ ವರ್ಗ ೪", "square"),

    # --- hello ---
    ("ನಮಸ್ಕಾರ ಪ್ರಪಂಚ", "hello"),
    ("ಹಲೋ ವರ್ಲ್ಡ್", "hello"),
    ("ನಮಸ್ಕಾರ ಎಲ್ಲರಿಗೂ", "hello"),
    ("ಹಲೋ", "hello"),
    ("ಹೆಲ್ಲೊ ವರ್ಲ್ಡ್", "hello"),
    ("ನಮಸ್ಕಾರ", "hello"),
    ("ನಮಸ್ಕಾರ ಜಗತ್ತು", "hello"),
    ("ನಮಸ್ಕಾರ ವಿಶ್ವ", "hello"),

    # --- print_num ---
    ("೫ ಮುದ್ರಿಸು", "print_num"),
    ("೧೦೦ ತೋರಿಸು", "print_num"),
    ("ಹತ್ತು ಮುದ್ರಿಸು", "print_num"),
    ("೪೨ ಪ್ರಿಂಟ್ ಮಾಡು", "print_num"),
    ("ಐದು ತೋರಿಸು", "print_num"),
    ("೭ ಮುದ್ರಿಸು", "print_num"),
    ("೨೫ ಮುದ್ರಿಸು", "print_num"),
    ("ಹನ್ನೆರಡು ಮುದ್ರಿಸು", "print_num"),
    ("ಒಂಬತ್ತು ತೋರಿಸು", "print_num"),
    ("೯೯ ಮುದ್ರಿಸು", "print_num"),

    # --- list_ops ---
    ("ಪಟ್ಟಿ ಮಾಡು ೧ ೨ ೩", "list_ops"),
    ("ಪಟ್ಟಿ ೧ ೨ ೩ ೪ ೫", "list_ops"),
    ("ಪಟ್ಟಿ ತೋರಿಸು", "list_ops"),
    ("ಪಟ್ಟಿ ಉದ್ದ ಎಷ್ಟು", "list_ops"),
    ("ಪಟ್ಟಿಯ ಮೊದಲ ಅಂಶ", "list_ops"),
    ("ಪಟ್ಟಿ ೧೦ ೨೦ ೩೦", "list_ops"),
]


# ---------------------------------------------------------------------------
# Code templates
# ---------------------------------------------------------------------------
TEMPLATES = {
    "add":       "{a} {b} ಕೂಡು ಮುದ್ರಿಸು.",
    "subtract":  "{a} {b} ಕಳೆ ಮುದ್ರಿಸು.",
    "multiply":  "{a} {b} ಗುಣಿಸು ಮುದ್ರಿಸು.",
    "divide":    "{a} {b} ಭಾಗಿಸು ಮುದ್ರಿಸು.",
    "square":    "ವರ್ಗ: ನಕಲು ಗುಣಿಸು ॥\n{a} ವರ್ಗ ಮುದ್ರಿಸು.",
    "hello":     '"ನಮಸ್ಕಾರ ಪ್ರಪಂಚ!" ಮುದ್ರಿಸು.',
    "print_num": "{a} ಮುದ್ರಿಸು.",
    "list_ops":  "[{items}] ಮುದ್ರಿಸು.",
}

# Default numbers when user doesn't provide enough
DEFAULTS = {"a": 5, "b": 3}


# ---------------------------------------------------------------------------
# NL Engine class
# ---------------------------------------------------------------------------
class KapilaNLEngine:
    """
    Natural Language → Kapila Code engine.

    Uses a PicoNN MLP trained on keyword features to classify intent,
    then generates Kapila code from templates.
    """

    def __init__(self):
        self.num_features = len(KEYWORDS)
        self.num_intents = len(INTENTS)
        self.model = None
        self.trained = False
        self.train_log = []

    def train(self, epochs=80, lr=0.05):
        """Train the intent classifier on built-in training data."""
        # input → 16 → num_intents (kept small for PicoNN scalar autograd speed)
        self.model = MLP(self.num_features, [16, self.num_intents])
        optimizer = Adam(self.model.parameters(), lr=lr)

        data = TRAINING_DATA.copy()
        self.train_log = []

        for epoch in range(epochs):
            random.shuffle(data)
            epoch_loss = 0.0

            for text, intent_name in data:
                # Forward
                features = [Value(f) for f in extract_features(text)]
                logits = self.model(features)
                target = INTENT_TO_IDX[intent_name]
                loss = cross_entropy_loss(logits, target)

                # Backward
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                epoch_loss += loss.data

            avg = epoch_loss / len(data)
            if epoch % 20 == 0:
                self.train_log.append(f"epoch {epoch}: loss={avg:.4f}")

        self.trained = True
        # Check accuracy
        correct = 0
        for text, intent_name in TRAINING_DATA:
            pred = self._classify(text)
            if pred == intent_name:
                correct += 1
        accuracy = correct / len(TRAINING_DATA)
        self.train_log.append(f"final accuracy: {accuracy:.1%} ({correct}/{len(TRAINING_DATA)})")
        return accuracy

    def _classify(self, text: str) -> str:
        """Classify text into an intent."""
        features = [Value(f) for f in extract_features(text)]
        logits = self.model(features)
        probs = softmax(logits)
        best_idx = max(range(len(probs)), key=lambda i: probs[i].data)
        return INTENTS[best_idx]

    def _confidence(self, text: str) -> float:
        """Get classification confidence."""
        features = [Value(f) for f in extract_features(text)]
        logits = self.model(features)
        probs = softmax(logits)
        return max(p.data for p in probs)

    def process(self, text: str) -> dict:
        """
        Process natural language input → Kapila code.

        Returns:
            {intent, confidence, code, numbers, aksharas}
        """
        if not self.trained:
            return {"error": "Engine not trained yet"}

        text = text.strip()
        if not text:
            return {"error": "Empty input"}

        intent = self._classify(text)
        confidence = self._confidence(text)
        numbers = extract_numbers(text)
        aksharas = split_aksharas(text)

        # Generate code from template
        code = self._generate_code(intent, numbers)

        return {
            "intent": intent,
            "confidence": round(confidence, 3),
            "code": code,
            "numbers": numbers,
            "aksharas": aksharas,
        }

    def _generate_code(self, intent: str, numbers: list) -> str:
        """Generate Kapila code from intent and extracted parameters."""
        template = TEMPLATES.get(intent, "")

        if intent in ("add", "subtract", "multiply", "divide"):
            a = to_kannada_num(numbers[0]) if len(numbers) >= 1 else to_kannada_num(DEFAULTS["a"])
            b = to_kannada_num(numbers[1]) if len(numbers) >= 2 else to_kannada_num(DEFAULTS["b"])
            return template.format(a=a, b=b)

        elif intent == "square":
            a = to_kannada_num(numbers[0]) if numbers else to_kannada_num(DEFAULTS["a"])
            return template.format(a=a)

        elif intent == "print_num":
            a = to_kannada_num(numbers[0]) if numbers else to_kannada_num(DEFAULTS["a"])
            return template.format(a=a)

        elif intent == "hello":
            return template

        elif intent == "list_ops":
            if numbers:
                items = " ".join(to_kannada_num(n) for n in numbers)
            else:
                items = "೧ ೨ ೩ ೪ ೫"
            return template.format(items=items)

        return template


# ---------------------------------------------------------------------------
# Module-level singleton — trained once at import
# ---------------------------------------------------------------------------
_engine = None


def get_engine() -> KapilaNLEngine:
    """Get or create the singleton NL engine (trained on first call)."""
    global _engine
    if _engine is None:
        _engine = KapilaNLEngine()
        _engine.train(epochs=80, lr=0.05)
    return _engine


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Kapila NL Engine — Training...")
    engine = get_engine()
    for line in engine.train_log:
        print(f"  {line}")

    test_inputs = [
        # Basic operations
        "ಐದು ಮತ್ತು ಮೂರು ಕೂಡಿಸು",
        "೧೦ ೩ ಕಳೆ",
        "೬ ೭ ಗುಣಿಸು",
        "೧೦೦ ೪ ಭಾಗಿಸು",
        "೫ ವರ್ಗ",
        "ನಮಸ್ಕಾರ ಪ್ರಪಂಚ",
        "೪೨ ಮುದ್ರಿಸು",
        "ಪಟ್ಟಿ ೧ ೨ ೩",
        # The tricky ones — "ಮತ್ತು" with non-add intents
        "ಸಂಖ್ಯಾ ರೇಖೆಯ ಮೊದಲ ಮತ್ತು ಹನ್ನೆರಡನೇ ಸಂಖ್ಯೆಗಳನ್ನು ಗುಣಿಸು",
        "೧೦ ಮತ್ತು ೩ ಕಳೆ",
        "ಹನ್ನೆರಡು ಮತ್ತು ಮೂರು ಭಾಗಿಸು",
        # Ordinals
        "ಐದನೇ ಸಂಖ್ಯೆಯ ವರ್ಗ",
        "ಮೊದಲ ಮತ್ತು ಎರಡನೇ ಸಂಖ್ಯೆಗಳನ್ನು ಕೂಡು",
    ]

    print("\nTest Results:")
    print("-" * 70)
    for inp in test_inputs:
        result = engine.process(inp)
        print(f"  Input:   {inp}")
        print(f"  Intent:  {result['intent']} ({result['confidence']:.0%})")
        print(f"  Numbers: {result['numbers']}")
        print(f"  Code:    {result['code']}")
        print()
