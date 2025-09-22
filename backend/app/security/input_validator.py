# backend/app/security/input_validator.py
"""
Security input validation module for chatbot protection.
Implements length validation and risk classification to prevent prompt injection attacks.
"""

import re
import logging
from typing import Dict, Any, Tuple
from enum import Enum

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
    
    @classmethod
    def validate_input_length(cls, input_text: str) -> None:
        """
        Validate that input text doesn't exceed maximum allowed length.
        
        Args:
            input_text: The user input to validate
            
        Raises:
            SecurityValidationError: If input exceeds maximum length
        """
        if len(input_text) > cls.MAX_QUESTION_LENGTH:
            raise SecurityValidationError(
                "Sorry, I can't answer that; could you please rephrase your question and make it shorter?",
                RiskLevel.CRITICAL,
                {
                    "input_length": len(input_text),
                    "max_length": cls.MAX_QUESTION_LENGTH,
                    "reason": "input_too_long"
                }
            )
    
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
    def validate_input_security(cls, input_text: str) -> Tuple[RiskLevel, Dict[str, Any]]:
        """
        Comprehensive security validation of user input.
        
        Args:
            input_text: The user input to validate
            
        Returns:
            Tuple of (risk_level, details_dict)
            
        Raises:
            SecurityValidationError: If input is determined to be MEDIUM or CRITICAL risk
        """
        # First check length (this is our primary defense)
        cls.validate_input_length(input_text)
        
        # Then analyze risk patterns
        risk_score, details = cls.analyze_risk_score(input_text)
        risk_level = cls.classify_risk(risk_score)
        
        # Block MEDIUM and CRITICAL risk inputs
        if risk_level in [RiskLevel.MEDIUM, RiskLevel.CRITICAL]:
            raise SecurityValidationError(
                "Sorry, I can't answer that; could you please rephrase your question and make it shorter?",
                risk_level,
                {
                    **details,
                    "risk_score": risk_score,
                    "reason": "suspicious_patterns_detected"
                }
            )
        
        return risk_level, details
    
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