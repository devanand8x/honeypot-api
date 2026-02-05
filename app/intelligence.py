"""
Intelligence Extraction Module
Extract bank accounts, UPI IDs, phone numbers, phishing links
"""

import re
from typing import List, Optional
from app.models import SessionIntelligence as ExtractedIntelligence


# Regex patterns for intelligence extraction
PATTERNS = {
    # Bank account: 9-18 digits
    "bank_account": r"\b\d{9,18}\b",
    
    # IFSC Code: 4 letters + 0 + 6 alphanumeric
    "ifsc": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    
    # UPI ID: word@provider format
    "upi_id": r"\b[\w\.\-]+@[a-zA-Z]{2,}\b",
    
    # Indian phone: +91 or starting with 6-9
    "phone": r"(?:\+91[\-\s]?)?[6-9]\d{9}\b",
    
    # URLs
    "url": r"https?://[^\s<>\"{}|\\^`\[\]]+",
    
    # Email
    "email": r"\b[\w\.\-]+@[\w\.\-]+\.[a-zA-Z]{2,}\b",
    
    # Verification Code: 6 digits (for Social Engineering/OTPs)
    "verification_code": r"\b\d{6}\b"
}

# Keywords that indicate suspicious intent
SUSPICIOUS_KEYWORDS = [
    "urgent", "immediately", "blocked", "suspended", "verify",
    "otp", "pin", "password", "cvv", "transfer", "send money",
    "prize", "winner", "lottery", "refund", "cashback",
    "click here", "update now", "confirm", "validate",
    "bank account", "upi", "payment", "amount",
    "arrest", "legal action", "police", "fine", "penalty",
    "customer care", "helpline", "support",
    "jaldi", "turant", "abhi", "block", "band"
]


def extract_intelligence(text: str, existing: Optional[ExtractedIntelligence] = None) -> ExtractedIntelligence:
    """
    Extract all intelligence from a text message
    
    Args:
        text: The message text to analyze
        existing: Optional existing intelligence to merge with
    
    Returns:
        ExtractedIntelligence (SessionIntelligence) object with extracted data
    """
    # Input validation
    if not text or not isinstance(text, str):
        return existing if existing else ExtractedIntelligence()
    
    if existing is None:
        existing = ExtractedIntelligence()
    
    text_upper = text.upper()
    text_lower = text.lower()
    
    # Extract bank accounts (handles spaces/dashes if they form a 9-18 digit number)
    # First, look for the raw pattern
    raw_accounts = re.findall(PATTERNS["bank_account"], text)
    
    # Second, look for formatted numbers like "1234 5678 9012" or "1234-5678-9012"
    # We look for groups of 3-4 digits separated by space or dash
    formatted_matches = re.findall(r"\b(?:\d{3,4}[\s\-]?){3,6}\b", text)
    for fm in formatted_matches:
        cleaned = re.sub(r"[\s\-]", "", fm)
        if 9 <= len(cleaned) <= 18:
            raw_accounts.append(fm) # Keep original for display or cleaned for consistency
            
    if raw_accounts:
        # Filter and normalize
        filtered = []
        for a in raw_accounts:
            cleaned = re.sub(r"[\s\-]", "", a)
            # Validation: 
            # 1. Not a year (starting with 20)
            # 2. Not a typical Indian Mobile Number (10 digits starting with 6-9)
            is_mobile = len(cleaned) == 10 and cleaned[0] in "6789"
            if (not cleaned.startswith("20") or len(cleaned) > 4) and not is_mobile:
                filtered.append(cleaned)
        existing.bankAccounts = list(set(existing.bankAccounts + filtered))
    
    # Extract UPI IDs
    upi_ids = re.findall(PATTERNS["upi_id"], text, re.IGNORECASE)
    true_domains = [".com", ".net", ".org", ".gov", ".edu", ".in", ".co"]
    # Improved UPI filtering: only keep if it looks like a provider part (common VPA suffixes)
    common_vpa_suffixes = ["@ybl", "@paytm", "@oksbi", "@okaxis", "@okicici", "@ibl", "@apl", "@axl"]
    upi_ids = [u for u in upi_ids if not any(u.lower().endswith(ext) for ext in true_domains) or any(u.lower().endswith(s) for s in common_vpa_suffixes)]
    existing.upiIds = list(set(existing.upiIds + upi_ids))
    
    # Extract phone numbers
    # Support more formats including +91 98765 43210
    raw_phones = re.findall(r"(?:\+91[\-\s]?)?[6-9]\d{1,4}[\-\s]?\d{1,4}[\-\s]?\d{1,4}\b", text)
    phones = raw_phones
    # Also catch any 10 digit number starting with 6-9
    just_digits = re.findall(r"\b[6-9]\d{9}\b", text)
    phones.extend(just_digits)
    # Clean up phone numbers (remove dashes, spaces, +91)
    cleaned_phones = []
    for p in phones:
        cleaned = re.sub(r"[\s\-\+]", "", p)
        if cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        if len(cleaned) == 10:
            cleaned_phones.append(cleaned)
    existing.phoneNumbers = list(set(existing.phoneNumbers + cleaned_phones))
    
    # Extract URLs (potential phishing links)
    urls = re.findall(PATTERNS["url"], text)
    # Filter out known safe domains
    safe_domains = ["google.com", "facebook.com", "twitter.com", "gov.in", "rbi.org.in"]
    urls = [u for u in urls if not any(safe in u.lower() for safe in safe_domains)]
    existing.phishingLinks = list(set(existing.phishingLinks + urls))
    
    # Extract suspicious keywords found in text
    found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in text_lower]
    
    # Also include 6-digit verification codes as suspicious keywords
    codes = re.findall(PATTERNS["verification_code"], text)
    if codes:
        found_keywords.extend([f"Code: {c}" for c in codes])
        
    existing.suspiciousKeywords = list(set(existing.suspiciousKeywords + found_keywords))
    
    return existing


def merge_intelligence(intel1: ExtractedIntelligence, intel2: ExtractedIntelligence) -> ExtractedIntelligence:
    """Merge two intelligence objects"""
    return ExtractedIntelligence(
        bankAccounts=list(set(intel1.bankAccounts + intel2.bankAccounts)),
        upiIds=list(set(intel1.upiIds + intel2.upiIds)),
        phoneNumbers=list(set(intel1.phoneNumbers + intel2.phoneNumbers)),
        phishingLinks=list(set(intel1.phishingLinks + intel2.phishingLinks)),
        suspiciousKeywords=list(set(intel1.suspiciousKeywords + intel2.suspiciousKeywords))
    )


def intelligence_to_dict(intel: ExtractedIntelligence) -> dict:
    """Convert ExtractedIntelligence to dictionary for callback"""
    return {
        "bankAccounts": intel.bankAccounts,
        "upiIds": intel.upiIds,
        "phishingLinks": intel.phishingLinks,
        "phoneNumbers": intel.phoneNumbers,
        "suspiciousKeywords": intel.suspiciousKeywords
    }

def is_repetitive(history: list, threshold: int = 3) -> bool:
    """
    Detect if the scammer is repeating themselves.
    Returns True if the last 'threshold' messages from scammer are highly similar.
    """
    scammer_msgs = [m.get("text", "").lower() for m in history if m.get("sender") == "scammer"]
    if len(scammer_msgs) < threshold:
        return False
    
    last_n = scammer_msgs[-threshold:]
    
    def get_sim(s1, s2):
        w1, w2 = set(s1.split()), set(s2.split())
        if not w1 or not w2: return 0
        return len(w1 & w2) / max(len(w1), len(w2))

    all_similar = True
    for i in range(len(last_n) - 1):
        if get_sim(last_n[i], last_n[i+1]) < 0.7:
            all_similar = False
            break
            
    return all_similar
