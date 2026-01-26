"""
Scam Detection Module
Detects scam intent using keyword matching and pattern analysis
"""

import re
from typing import Tuple, List


# Scam indicator keywords (English + Hindi)
URGENCY_KEYWORDS = [
    # English
    "immediately", "urgent", "now", "today", "hurry", "quick", "fast",
    "limited time", "act now", "don't delay", "expire", "deadline",
    "expiring", "last chance", "final notice", "action required",
    "attention", "alert", "notice", "overdue", "disconnection",
    # Hindi
    "turant", "jaldi", "abhi", "aaj hi", "fauran", "saavdhan"
]

THREAT_KEYWORDS = [
    # English
    "blocked", "suspended", "locked", "frozen", "deactivated",
    "legal action", "arrest", "police", "court", "penalty", "fine",
    "case filed", "warrant", "crime", "kyc", "expire", "expiry",
    "suspicious", "unusual", "unauthorized", "fraud", "hacked",
    "compromised", "security alert", "warning", "investigation",
    "under surveillance", "warrant issued", "held", "detained",
    "lapsed", "closed", "deactivated", "disabled", "invalid",
    # Hindi
    "band", "block", "arrest", "jail", "thana", "case"
]

FINANCIAL_KEYWORDS = [
    # English
    "bank account", "otp", "pin", "password", "cvv", "card number",
    "upi", "transfer", "payment", "refund", "cashback", "prize",
    "lottery", "winner", "reward", "bonus", "free money",
    "won", "congratulations", "claim", "lakh", "crore", "jackpot",
    "atm", "credit card", "debit card", "loan", "approved", "selected",
    "iphone", "samsung", "gift", "voucher", "offer", "shopping",
    "salary", "income", "profit", "investment", "return", "double",
    "insurance", "premium", "policy", "duty", "tax", "fee", "charge",
    "electricity", "bill", "light", "power", "meter", "gold", "coin",
    "car", "bike", "laptop", "job", "hiring", "vacancy", "interview",
    # Hindi
    "khata", "paisa", "rupees", "rs", "inaam", "naukri"
]

AUTHORITY_KEYWORDS = [
    "rbi", "reserve bank", "sbi", "hdfc", "icici", "axis",
    "government", "income tax", "customs", "police", "cbi",
    "customer care", "support", "helpline", "official"
]

REQUEST_KEYWORDS = [
    "share", "send", "give", "provide", "enter", "click", "verify",
    "confirm", "update", "validate", "submit", "link", "http", "www",
    "open", "visit", "login", "register", "call", "contact", "dial",
    "press", "tap", "download", "install",
    # Hindi
    "bhejo", "do", "batao", "dijiye", "karo"
]

# Suspicious patterns
PATTERNS = {
    "upi_request": r"(share|send|give).*(upi|vpa|@)",
    "otp_request": r"(share|send|give|enter).*(otp|code|pin)",
    "link_click": r"(click|open|visit).*(link|url|http)",
    "money_request": r"(send|transfer|pay).*(money|amount|rs|₹|\d+)",
    "kyc_scam": r"(kyc|update|verify).*(account|bank|details|wallet)",
    "job_scam": r"(job|work|hiring|vacancy|earning|salary).*(daily|guaranteed|apply|hr)",
    "electricity_scam": r"(electricity|bill|light|power).*(disconnect|unpaid|cut|update)",
    "customs_scam": r"(customs|parcel|package|delivery).*(hold|held|duty|tax|fee)",
    "account_threat": r"(account|khata).*(block|suspend|freeze|band)",
    "prize_scam": r"(won|winner|prize|lottery|congratulations).*(lakh|crore|rs|₹|\d+)"
}


def detect_scam(text: str) -> Tuple[bool, float, List[str], str]:
    """
    Detect if a message is a scam
    
    Args:
        text: The message text to analyze
    
    Returns:
        Tuple of (is_scam, confidence_score, suspicious_keywords, notes)
    """
    # Input validation
    if not text or not isinstance(text, str):
        return False, 0.0, [], "No text provided"
    
    text_lower = text.lower()
    
    score = 0.0
    detected_keywords = []
    notes_parts = []
    
    # Check urgency keywords (weight: 0.15)
    urgency_found = [kw for kw in URGENCY_KEYWORDS if kw in text_lower]
    if urgency_found:
        score += 0.15
        detected_keywords.extend(urgency_found)
        notes_parts.append("urgency tactics")
    
    # Check threat keywords (weight: 0.25)
    threat_found = [kw for kw in THREAT_KEYWORDS if kw in text_lower]
    if threat_found:
        score += 0.25
        detected_keywords.extend(threat_found)
        notes_parts.append("threatening language")
    
    # Check financial keywords (weight: 0.20)
    financial_found = [kw for kw in FINANCIAL_KEYWORDS if kw in text_lower]
    if financial_found:
        score += 0.20
        detected_keywords.extend(financial_found)
        notes_parts.append("financial terms")
    
    # Check authority impersonation (weight: 0.15)
    authority_found = [kw for kw in AUTHORITY_KEYWORDS if kw in text_lower]
    if authority_found:
        score += 0.15
        detected_keywords.extend(authority_found)
        notes_parts.append("authority impersonation")
    
    # Check request keywords (weight: 0.10)
    request_found = [kw for kw in REQUEST_KEYWORDS if kw in text_lower]
    if request_found:
        score += 0.10
        detected_keywords.extend(request_found)
        notes_parts.append("information request")
    
    # Check patterns (weight: 0.15 each, max 0.30)
    pattern_matches = 0
    for pattern_name, pattern in PATTERNS.items():
        if re.search(pattern, text_lower):
            pattern_matches += 1
            notes_parts.append(f"pattern: {pattern_name}")
    score += min(pattern_matches * 0.15, 0.30)
    
    # Final decision
    is_scam = score >= 0.30
    confidence = min(score, 1.0)
    
    notes = "Scammer used " + ", ".join(notes_parts) if notes_parts else "No scam indicators"
    
    return is_scam, confidence, list(set(detected_keywords)), notes


def analyze_conversation_history(history: list) -> Tuple[float, List[str]]:
    """
    Analyze full conversation history for cumulative scam detection
    """
    total_score = 0.0
    all_keywords = []
    
    for msg in history:
        if msg.get("sender") == "scammer":
            _, score, keywords, _ = detect_scam(msg.get("text", ""))
            total_score += score * 0.5  # Reduced weight for history
            all_keywords.extend(keywords)
    
    return min(total_score, 1.0), list(set(all_keywords))
