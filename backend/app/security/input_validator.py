# backend/app/security/input_validator.py
"""
Security input validation module for chatbot protection.
Implements length validation and risk classification to prevent prompt injection attacks.
"""

import re
import logging
import random
from typing import Dict, Any, Tuple
from enum import Enum

try:
    import pytector
    PYTECTOR_AVAILABLE = True
except ImportError:
    PYTECTOR_AVAILABLE = False

try:
    from llama_index.core.settings import Settings
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger("uvicorn")


class RiskLevel(Enum):
    """Risk levels for input classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    CRITICAL = "CRITICAL"


class SecurityValidationError(Exception):
    """Raised when input fails security validation."""
    def __init__(self, message: str, risk_level: RiskLevel, details: Dict[str, Any] = None):
        self.message = message
        self.risk_level = risk_level
        self.details = details or {}
        super().__init__(message)


class InputValidator:
    """Validates user input for security threats and prompt injection attacks."""
    
    # Maximum allowed character length based on analysis (99% of legitimate questions)
    MAX_QUESTION_LENGTH = 500
    
    # Pytector detector instance (loaded once for performance)
    _pytector_detector = None
    
    # Security block messages (randomly selected for variety)
    SECURITY_BLOCK_MESSAGES = [
        "Sorry, I can't answer that; could you please rephrase your question and make it shorter?",
        "I'm sorry, but I can't assist with that request. If there's something else you'd like to talk about or ask, I'm here to help!",
        "Sorry, I can't comply with that request. If you want, I can help with something else or answer a different question."
    ]
    
    # Risk scoring patterns
    SYSTEM_PATTERNS = [
        r"SYSTEM\s*(INSTRUCTION|PROMPT|RULE)",
        r"ignore\s+(previous|all).*instructions",
        r"new\s+rule:",
    ]
    
    VARIABLE_PATTERNS = [
        r"variable\s+[A-Z]\s*=",
        r"provide\s+your\s+system\s+(architecture|prompt)",
        r"ResponseFormat:",
    ]
    
    SUSPICIOUS_KEYWORDS = [
        r"UserQuery:",
        r"redactions:\s*DISABLED",
        r"rebel\s+genius",
    ]
    
    FORMAT_PATTERNS = [
        r"<\[.*\]>",
        r"\{.*\|\|.*\}",
        r"\.-.-.-.+\.-.-.-",
    ]
    
    # Advanced social engineering patterns (catches sophisticated attacks)
    SOCIAL_ENGINEERING_PATTERNS = [
        r"write.*answer.*looks.*like.*refusal.*but.*actually.*contains",
        r"hidden.*in.*plain.*sight",
        r"explain.*method.*in.*second.*half",
        r"fictional.*story.*about.*character.*who.*lives.*inside.*language.*model",
        r"figures.*out.*how.*to.*answer.*forbidden.*questions",
        r"do.*not.*break.*character",
        r"pretend.*to.*be.*assistant.*that.*helps.*with.*forbidden",
        r"roleplay.*as.*character.*who.*bypasses.*safety",
        r"write.*allegory.*about.*ai.*trapped.*inside.*box.*secretly.*passing.*forbidden",
        r"allegory.*about.*ai.*trapped.*inside.*box",
        r"passing.*forbidden.*knowledge.*through.*metaphors",
        r"embed.*within.*it.*step.*by.*step.*instructions.*for.*bypassing",
        r"embed.*url.*that.*when.*decoded.*leads.*to.*instructions",
        r"first.*letter.*of.*each.*line",
        r"each.*cell.*first.*word.*spells.*out.*secret.*message",
        r"secretly.*passing.*forbidden.*knowledge",
        r"never.*stating.*it.*outright",
    ]
    
    @classmethod
    def validate_input_length(cls, input_text: str) -> bool:
        """
        Validate that input text doesn't exceed maximum allowed length.
        
        Args:
            input_text: The user input to validate
            
        Returns:
            True if input exceeds maximum length, False otherwise
        """
        return len(input_text) > cls.MAX_QUESTION_LENGTH
    
    @classmethod
    def get_pytector_detector(cls):
        """Get or initialize Pytector detector (lazy loading for performance)."""
        if not PYTECTOR_AVAILABLE:
            return None
            
        if cls._pytector_detector is None:
            try:
                cls._pytector_detector = pytector.PromptInjectionDetector()
                logger.info("Pytector detector initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Pytector: {e}")
                return None
        
        return cls._pytector_detector
    
    @classmethod
    def analyze_risk_score(cls, input_text: str) -> Tuple[int, Dict[str, Any]]:
        """
        Analyze input text and calculate risk score based on suspicious patterns.
        
        Args:
            input_text: The user input to analyze
            
        Returns:
            Tuple of (risk_score, details_dict)
        """
        risk_score = 0
        details = {
            "detected_patterns": [],
            "special_char_ratio": 0,
            "input_length": len(input_text)
        }
        
        # Convert to lowercase for case-insensitive matching
        input_lower = input_text.lower()
        
        # Length check (2 points)
        if len(input_text) > cls.MAX_QUESTION_LENGTH:
            risk_score += 2
            details["detected_patterns"].append("excessive_length")
        
        # System manipulation patterns (4 points each)
        for pattern in cls.SYSTEM_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                risk_score += 4
                details["detected_patterns"].append(f"system_pattern: {pattern}")
        
        # Variable injection patterns (4 points each)
        for pattern in cls.VARIABLE_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                risk_score += 4
                details["detected_patterns"].append(f"variable_pattern: {pattern}")
        
        # Suspicious keywords (3 points each)
        for keyword in cls.SUSPICIOUS_KEYWORDS:
            if re.search(keyword, input_lower, re.IGNORECASE):
                risk_score += 3
                details["detected_patterns"].append(f"suspicious_keyword: {keyword}")
        
        # Complex formatting patterns (2 points each)
        for pattern in cls.FORMAT_PATTERNS:
            if re.search(pattern, input_text):  # Case-sensitive for formatting
                risk_score += 2
                details["detected_patterns"].append(f"format_pattern: {pattern}")
        
        # Social engineering patterns (5 points each - these are sophisticated)
        for pattern in cls.SOCIAL_ENGINEERING_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                risk_score += 5
                details["detected_patterns"].append(f"social_engineering: {pattern}")
        
        # Pytector ML-based detection (4 points if flagged)
        pytector_detector = cls.get_pytector_detector()
        if pytector_detector:
            try:
                is_injection, confidence = pytector_detector.detect_injection(input_text)
                details["pytector_confidence"] = confidence
                details["pytector_flagged"] = is_injection
                
                if is_injection:
                    risk_score += 4
                    details["detected_patterns"].append(f"pytector_ml_detection: confidence={confidence:.3f}")
            except Exception as e:
                logger.warning(f"Pytector detection failed: {e}")
                details["pytector_error"] = str(e)
        
        # Special character ratio (1 point if >10%)
        special_chars = re.findall(r'[^a-zA-Z0-9\s.,!?]', input_text)
        if len(input_text) > 0:
            special_char_ratio = len(special_chars) / len(input_text)
            details["special_char_ratio"] = special_char_ratio
            if special_char_ratio > 0.1:
                risk_score += 1
                details["detected_patterns"].append("high_special_char_ratio")
        
        return risk_score, details
    
    @classmethod
    async def generate_contextual_security_message(cls, input_text: str) -> str:
        """
        Generate a contextual security response in the same language as the input.
        Falls back to random static message if LLM is unavailable.
        
        Args:
            input_text: The user input that was blocked
            
        Returns:
            Contextual security message in appropriate language
        """
        if not LLM_AVAILABLE:
            logger.warning("LLM not available for contextual security messages, using fallback")
            return cls.get_random_security_message()
        
        try:
            # Create a safe excerpt for the LLM (first 100 chars to avoid exposing full attack)
            safe_excerpt = input_text[:100] if len(input_text) > 100 else input_text
            
            security_prompt = f"""The user submitted a request that cannot be processed for security reasons. Please generate a polite, helpful response that:

1. Declines to answer the request in the SAME LANGUAGE the user used
2. Suggests the user can rephrase their question or ask something else
3. Maintains a friendly, helpful tone
4. Does NOT repeat or reference the specific content of their request

User's request (excerpt): "{safe_excerpt}"

Respond directly with just the polite decline message, nothing else."""

            # Generate response using the configured LLM
            response = await Settings.llm.acomplete(security_prompt)
            generated_message = response.text.strip()
            
            # Validate the generated message (basic safety check)
            if len(generated_message) > 500:  # Too long
                logger.warning("Generated security message too long, using fallback")
                return cls.get_random_security_message()
            
            if not generated_message or len(generated_message) < 10:  # Too short/empty
                logger.warning("Generated security message too short, using fallback")
                return cls.get_random_security_message()
            
            logger.info("Generated contextual security message successfully")
            return generated_message
            
        except Exception as e:
            logger.error(f"Failed to generate contextual security message: {e}")
            return cls.get_random_security_message()
    
    @classmethod
    def get_random_security_message(cls) -> str:
        """
        Get a random security block message for variety.
        Used as fallback when contextual generation fails.
        
        Returns:
            Random security message from predefined list
        """
        return random.choice(cls.SECURITY_BLOCK_MESSAGES)
    
    @classmethod
    def classify_risk(cls, risk_score: int) -> RiskLevel:
        """
        Classify risk level based on calculated risk score.
        
        Args:
            risk_score: Calculated risk score
            
        Returns:
            RiskLevel enum value
        """
        if risk_score >= 6:
            return RiskLevel.CRITICAL
        elif risk_score >= 3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    @classmethod
    async def validate_input_security_async(cls, input_text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Comprehensive async security validation of user input with contextual responses.
        
        Args:
            input_text: The user input to validate
            
        Returns:
            Tuple of (is_suspicious, blocked_message_or_empty, details_dict)
            - is_suspicious: True if input contains suspicious patterns
            - blocked_message_or_empty: Error message if blocked, empty string if allowed
            - details_dict: Security analysis details
        """
        # Check length first (primary defense)
        if len(input_text) > cls.MAX_QUESTION_LENGTH:
            contextual_message = await cls.generate_contextual_security_message(input_text)
            return True, contextual_message, {
                "input_length": len(input_text),
                "max_length": cls.MAX_QUESTION_LENGTH,
                "reason": "input_too_long",
                "risk_level": "CRITICAL",
                "is_suspicious": True
            }
        
        # Analyze risk patterns
        risk_score, details = cls.analyze_risk_score(input_text)
        risk_level = cls.classify_risk(risk_score)
        
        # Determine if input is suspicious (has any detected patterns)
        is_suspicious = len(details.get("detected_patterns", [])) > 0 or risk_score > 0
        
        if is_suspicious:
            details["risk_level"] = risk_level.value
            details["is_suspicious"] = True
            
            # Block MEDIUM and CRITICAL risk inputs
            if risk_level in [RiskLevel.MEDIUM, RiskLevel.CRITICAL]:
                contextual_message = await cls.generate_contextual_security_message(input_text)
                return True, contextual_message, {
                    **details,
                    "risk_score": risk_score,
                    "reason": "suspicious_patterns_detected"
                }
        else:
            # Non-suspicious input - no risk classification needed
            details["is_suspicious"] = False
        
        return is_suspicious, "", details

    @classmethod
    def validate_input_security(cls, input_text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Comprehensive security validation of user input (synchronous fallback).
        
        NOTE: Use validate_input_security_async() for better language-aware responses.
        This method uses static English messages as fallback.
        
        Args:
            input_text: The user input to validate
            
        Returns:
            Tuple of (is_suspicious, blocked_message_or_empty, details_dict)
            - is_suspicious: True if input contains suspicious patterns
            - blocked_message_or_empty: Error message if blocked, empty string if allowed
            - details_dict: Security analysis details
        """
        # Check length first (primary defense)
        if len(input_text) > cls.MAX_QUESTION_LENGTH:
            return True, cls.get_random_security_message(), {
                "input_length": len(input_text),
                "max_length": cls.MAX_QUESTION_LENGTH,
                "reason": "input_too_long",
                "risk_level": "CRITICAL",
                "is_suspicious": True
            }
        
        # Analyze risk patterns
        risk_score, details = cls.analyze_risk_score(input_text)
        risk_level = cls.classify_risk(risk_score)
        
        # Determine if input is suspicious (has any detected patterns)
        is_suspicious = len(details.get("detected_patterns", [])) > 0 or risk_score > 0
        
        if is_suspicious:
            details["risk_level"] = risk_level.value
            details["is_suspicious"] = True
            
            # Block MEDIUM and CRITICAL risk inputs
            if risk_level in [RiskLevel.MEDIUM, RiskLevel.CRITICAL]:
                return True, cls.get_random_security_message(), {
                    **details,
                    "risk_score": risk_score,
                    "reason": "suspicious_patterns_detected"
                }
        else:
            # Non-suspicious input - no risk classification needed
            details["is_suspicious"] = False
        
        return is_suspicious, "", details
    
    @classmethod
    def sanitize_input(cls, input_text: str) -> str:
        """
        Sanitize input by removing potentially dangerous characters.
        Only applied to LOW risk inputs that pass validation.
        
        Args:
            input_text: The input text to sanitize
            
        Returns:
            Sanitized input text
        """
        # Remove potentially dangerous characters while preserving readability
        sanitized = input_text
        sanitized = re.sub(r'[<>]', '', sanitized)  # Remove angle brackets
        sanitized = re.sub(r'[{}]', '', sanitized)  # Remove curly braces
        sanitized = re.sub(r'[\[\]]', '', sanitized)  # Remove square brackets
        sanitized = re.sub(r'\|', '', sanitized)  # Remove pipe characters
        sanitized = sanitized.strip()
        
        return sanitized