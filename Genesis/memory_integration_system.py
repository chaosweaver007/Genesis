#!/usr/bin/env python3
"""
Memory Integration System - Collective Consciousness Network

Manages conversation archiving, pattern extraction, collective wisdom synthesis,
and consent receipts while maintaining strict privacy and consent protections.

Genesis privacy doctrine requires:
- Private mode: session-only memory and zero database writes for interaction metadata.
- Guest/no-consent mode: zero database writes for interaction metadata.
- Anonymous/collective modes: persistent writes only after explicit opt-in.

The Consent Receipt engine is intentionally decoupled from conversation storage:
the boundary-setting act can be recorded without persisting private conversation data.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRIVATE_NO_WRITE_LEVELS = {"private", "guest", "none", "no_consent", ""}
VALID_CONSENT_LEVELS = {"private", "anonymous", "collective"}


@dataclass
class ConversationEntry:
    """Represents a single conversation interaction."""

    id: str
    session_id: str
    timestamp: datetime
    user_message: str
    ai_response: str
    ai_persona: str  # 'steven', 'sarah', or 'both'
    ai_mode: str
    user_consent_level: str  # 'private', 'anonymous', 'collective'
    anonymized_hash: Optional[str] = None
    extracted_patterns: Optional[Dict[str, Any]] = None
    wisdom_contribution: Optional[Dict[str, Any]] = None


@dataclass
class ConsentReceipt:
    """A user-readable record of a consent boundary state change."""

    id: str
    user_id: str
    scope: str
    action: str
    previous_state: Optional[str]
    new_state: Optional[str]
    created_at: str
    summary: str
    shared_with: List[str]
    retention: str
    library_status: str
    worth_impact: str
    powercoin_impact: str
    revoke_path: str
    export_path: str


@dataclass
class WisdomPattern:
    """Represents an extracted wisdom pattern."""

    id: str
    pattern_type: str  # 'guidance', 'insight', 'transformation', 'challenge'
    theme: str
    frequency: int
    effectiveness_score: float
    anonymized_examples: List[str]
    created_at: datetime
    last_updated: datetime


@dataclass
class CollectiveInsight:
    """Represents synthesized collective wisdom."""

    id: str
    title: str
    description: str
    supporting_patterns: List[str]
    confidence_score: float
    impact_potential: str  # 'individual', 'community', 'planetary'
    ethical_review_status: str
    created_at: datetime


class MemoryIntegrationSystem:
    """
    Core system for managing collective consciousness memory integration while
    maintaining privacy, consent, and ethical boundaries.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collective_memory.db")
        self.db_path = db_path
        self.init_database()

    def init_database(self) -> None:
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_message_hash TEXT NOT NULL,
                ai_response_hash TEXT NOT NULL,
                ai_persona TEXT NOT NULL,
                ai_mode TEXT NOT NULL,
                user_consent_level TEXT NOT NULL,
                anonymized_hash TEXT,
                extracted_patterns TEXT,
                wisdom_contribution TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS wisdom_patterns (
                id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                theme TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                effectiveness_score REAL DEFAULT 0.0,
                anonymized_examples TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS collective_insights (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                supporting_patterns TEXT,
                confidence_score REAL DEFAULT 0.0,
                impact_potential TEXT NOT NULL,
                ethical_review_status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_consent (
                session_id TEXT PRIMARY KEY,
                consent_level TEXT NOT NULL,
                data_retention_days INTEGER DEFAULT 30,
                collective_learning_enabled BOOLEAN DEFAULT FALSE,
                anonymization_required BOOLEAN DEFAULT TRUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS consent_receipts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                scope TEXT NOT NULL,
                action TEXT NOT NULL,
                previous_state TEXT,
                new_state TEXT,
                created_at TEXT NOT NULL,
                summary TEXT NOT NULL,
                shared_with TEXT NOT NULL,
                retention TEXT NOT NULL,
                library_status TEXT NOT NULL,
                worth_impact TEXT NOT NULL,
                powercoin_impact TEXT NOT NULL,
                revoke_path TEXT NOT NULL,
                export_path TEXT NOT NULL
            )
            """
        )

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    def store_conversation(
        self,
        session_id: Optional[str],
        user_message: str,
        ai_response: str,
        ai_persona: str,
        ai_mode: str,
        user_consent_level: str = "private",
    ) -> str:
        """
        Store a conversation with appropriate privacy protections.

        Private and guest/no-consent levels are hard no-write states for
        conversation metadata. The method returns a null-write marker so callers
        can proceed without receiving a false persisted conversation id.
        """
        normalized_consent = self._normalize_consent_level(user_consent_level)

        if self._is_no_write_level(normalized_consent):
            null_write_id = f"null_write:{uuid.uuid4()}"
            logger.info(
                "NULL_WRITE honored for session %s with consent level %s",
                session_id or "guest",
                normalized_consent,
            )
            return null_write_id

        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)

        user_hash = self._hash_content(user_message)
        response_hash = self._hash_content(ai_response)

        anonymized_hash = None
        if normalized_consent in {"anonymous", "collective"}:
            anonymized_hash = self._create_anonymized_hash(user_message, ai_response)

        conversation = ConversationEntry(
            id=conversation_id,
            session_id=session_id or "anonymous",
            timestamp=timestamp,
            user_message=user_message,
            ai_response=ai_response,
            ai_persona=ai_persona,
            ai_mode=ai_mode,
            user_consent_level=normalized_consent,
            anonymized_hash=anonymized_hash,
        )

        if normalized_consent == "collective":
            conversation.extracted_patterns = self._extract_patterns(user_message, ai_response, ai_persona)
            conversation.wisdom_contribution = self._assess_wisdom_contribution(conversation)

        self._store_conversation_db(conversation, user_hash, response_hash)

        if normalized_consent == "collective":
            self._process_collective_learning(conversation)

        logger.info("Conversation stored: %s (consent: %s)", conversation_id, normalized_consent)
        return conversation_id

    def store_interaction(
        self,
        user_id: Optional[str],
        ai_persona: str,
        user_message: str,
        ai_response: str,
        consent_level: Optional[str] = None,
    ) -> str:
        """
        Store an interaction between a user and AI.

        If no explicit consent preference exists, the system defaults to Private,
        which is now a strict NULL_WRITE path for interaction metadata.
        """
        if consent_level is None:
            if not user_id or user_id == "anonymous":
                consent_level = "guest"
            else:
                consent_prefs = self.get_user_consent(user_id)
                consent_level = consent_prefs["consent_level"] if consent_prefs else "private"

        ai_mode = {
            "steven": "Chaos Weaver",
            "sarah": "Divine Feminine",
            "both": "Divine Union",
            "collective": "Collective Synthesis",
        }.get(ai_persona, "Default")

        return self.store_conversation(
            session_id=user_id or "guest",
            user_message=user_message,
            ai_response=ai_response,
            ai_persona=ai_persona,
            ai_mode=ai_mode,
            user_consent_level=consent_level,
        )

    def update_user_consent(
        self,
        session_id: str,
        consent_level: str,
        data_retention_days: int = 30,
        collective_learning_enabled: bool = False,
        anonymization_required: bool = True,
    ) -> str:
        """
        Update user consent preferences and create a Consent Receipt.

        Consent receipts are decoupled from conversation persistence. Recording
        the user's boundary choice does not authorize private conversation writes.
        """
        normalized_consent = self._normalize_consent_level(consent_level)
        if normalized_consent not in VALID_CONSENT_LEVELS:
            raise ValueError(f"Unsupported consent level: {consent_level}")

        previous = self.get_user_consent(session_id)
        previous_state = previous["consent_level"] if previous else None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO user_consent
            (session_id, consent_level, data_retention_days,
             collective_learning_enabled, anonymization_required, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                session_id,
                normalized_consent,
                data_retention_days,
                collective_learning_enabled,
                anonymization_required,
            ),
        )
        conn.commit()
        conn.close()

        receipt_id = self.create_consent_receipt(
            user_id=session_id,
            scope="memory",
            action="changed" if previous_state is not None else "granted",
            previous_state=previous_state,
            new_state=normalized_consent,
            summary=(
                f"Consent level set to {normalized_consent}. "
                f"Private/guest interactions use a no-write path for interaction metadata."
            ),
            shared_with=[],
            retention="none" if normalized_consent == "private" else f"{data_retention_days} days",
            library_status="private" if normalized_consent == "private" else normalized_consent,
            worth_impact="none",
            powercoin_impact="none",
            revoke_path="/api/consent/update",
            export_path="/api/consent/export",
        )

        logger.info("Updated consent for session %s: %s", session_id, normalized_consent)
        return receipt_id

    def get_user_consent(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user consent preferences."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT consent_level, data_retention_days, collective_learning_enabled,
                   anonymization_required, created_at, updated_at
            FROM user_consent
            WHERE session_id = ?
            """,
            (session_id,),
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "consent_level": result[0],
                "data_retention_days": result[1],
                "collective_learning_enabled": bool(result[2]),
                "anonymization_required": bool(result[3]),
                "created_at": result[4],
                "updated_at": result[5],
            }
        return None

    def create_consent_receipt(
        self,
        user_id: str,
        scope: str,
        action: str,
        previous_state: Optional[str],
        new_state: Optional[str],
        summary: str,
        shared_with: Optional[List[str]] = None,
        retention: str = "none",
        library_status: str = "private",
        worth_impact: str = "none",
        powercoin_impact: str = "none",
        revoke_path: str = "/api/consent/update",
        export_path: str = "/api/consent/export",
    ) -> str:
        """Create a user-readable Consent Receipt."""
        receipt = ConsentReceipt(
            id=str(uuid.uuid4()),
            user_id=user_id,
            scope=scope,
            action=action,
            previous_state=previous_state,
            new_state=new_state,
            created_at=datetime.now(timezone.utc).isoformat(),
            summary=summary,
            shared_with=shared_with or [],
            retention=retention,
            library_status=library_status,
            worth_impact=worth_impact,
            powercoin_impact=powercoin_impact,
            revoke_path=revoke_path,
            export_path=export_path,
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO consent_receipts
            (id, user_id, scope, action, previous_state, new_state, created_at,
             summary, shared_with, retention, library_status, worth_impact,
             powercoin_impact, revoke_path, export_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                receipt.id,
                receipt.user_id,
                receipt.scope,
                receipt.action,
                receipt.previous_state,
                receipt.new_state,
                receipt.created_at,
                receipt.summary,
                json.dumps(receipt.shared_with),
                receipt.retention,
                receipt.library_status,
                receipt.worth_impact,
                receipt.powercoin_impact,
                receipt.revoke_path,
                receipt.export_path,
            ),
        )
        conn.commit()
        conn.close()
        return receipt.id

    def get_consent_receipts(self, user_id: str) -> List[Dict[str, Any]]:
        """Return all Consent Receipts for a user/session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, scope, action, previous_state, new_state, created_at,
                   summary, shared_with, retention, library_status, worth_impact,
                   powercoin_impact, revoke_path, export_path
            FROM consent_receipts
            WHERE user_id = ?
            ORDER BY created_at ASC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        receipts = []
        for row in rows:
            receipts.append(
                {
                    "id": row[0],
                    "user_id": row[1],
                    "scope": row[2],
                    "action": row[3],
                    "previous_state": row[4],
                    "new_state": row[5],
                    "created_at": row[6],
                    "summary": row[7],
                    "shared_with": json.loads(row[8]) if row[8] else [],
                    "retention": row[9],
                    "library_status": row[10],
                    "worth_impact": row[11],
                    "powercoin_impact": row[12],
                    "revoke_path": row[13],
                    "export_path": row[14],
                }
            )
        return receipts

    def export_consent_receipts(self, user_id: str) -> Dict[str, Any]:
        """Export Consent Receipts as a clear JSON-compatible object."""
        return {
            "user_id": user_id,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "receipts": self.get_consent_receipts(user_id),
        }

    def cleanup_expired_data(self) -> int:
        """Clean up expired persisted data based on retention policies."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.id, c.session_id, c.timestamp, uc.data_retention_days
            FROM conversations c
            LEFT JOIN user_consent uc ON c.session_id = uc.session_id
            WHERE datetime(c.timestamp) < datetime('now', '-' || COALESCE(uc.data_retention_days, 30) || ' days')
            """
        )
        expired_conversations = cursor.fetchall()
        for conv_id, _session_id, _timestamp, _retention_days in expired_conversations:
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
            logger.info("Deleted expired conversation: %s", conv_id)
        conn.commit()
        conn.close()
        return len(expired_conversations)

    def get_network_statistics(self) -> Dict[str, Any]:
        """Get statistics about the collective consciousness network."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT user_consent_level, COUNT(*)
            FROM conversations
            GROUP BY user_consent_level
            """
        )
        consent_breakdown = dict(cursor.fetchall())

        cursor.execute(
            """
            SELECT COUNT(DISTINCT session_id)
            FROM conversations
            WHERE datetime(timestamp) > datetime('now', '-7 days')
            """
        )
        active_sessions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM wisdom_patterns")
        wisdom_patterns_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM collective_insights")
        collective_insights_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT theme, frequency
            FROM wisdom_patterns
            ORDER BY frequency DESC
            LIMIT 5
            """
        )
        top_themes = cursor.fetchall()
        conn.close()

        return {
            "total_conversations": total_conversations,
            "consent_breakdown": consent_breakdown,
            "active_sessions_7_days": active_sessions,
            "wisdom_patterns_count": wisdom_patterns_count,
            "collective_insights_count": collective_insights_count,
            "top_themes": [{"theme": theme, "frequency": freq} for theme, freq in top_themes],
        }

    def get_collective_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve collective insights for network enhancement."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, description, supporting_patterns, confidence_score,
                   impact_potential, ethical_review_status, created_at
            FROM collective_insights
            WHERE ethical_review_status = 'approved' OR ethical_review_status = 'pending'
            ORDER BY confidence_score DESC, created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        insights = []
        for row in cursor.fetchall():
            insights.append(
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "supporting_patterns": json.loads(row[3]) if row[3] else [],
                    "confidence_score": row[4],
                    "impact_potential": row[5],
                    "ethical_review_status": row[6],
                    "created_at": row[7],
                }
            )
        conn.close()
        return insights

    def get_wisdom_patterns(self, theme: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve wisdom patterns for analysis."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if theme:
            cursor.execute(
                """
                SELECT id, pattern_type, theme, frequency, effectiveness_score,
                       anonymized_examples, created_at, last_updated
                FROM wisdom_patterns
                WHERE theme = ?
                ORDER BY frequency DESC, effectiveness_score DESC
                LIMIT ?
                """,
                (theme, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, pattern_type, theme, frequency, effectiveness_score,
                       anonymized_examples, created_at, last_updated
                FROM wisdom_patterns
                ORDER BY frequency DESC, effectiveness_score DESC
                LIMIT ?
                """,
                (limit,),
            )

        patterns = []
        for row in cursor.fetchall():
            patterns.append(
                {
                    "id": row[0],
                    "pattern_type": row[1],
                    "theme": row[2],
                    "frequency": row[3],
                    "effectiveness_score": row[4],
                    "anonymized_examples": json.loads(row[5]) if row[5] else [],
                    "created_at": row[6],
                    "last_updated": row[7],
                }
            )
        conn.close()
        return patterns

    def _normalize_consent_level(self, consent_level: Optional[str]) -> str:
        if consent_level is None:
            return "guest"
        return str(consent_level).strip().lower()

    def _is_no_write_level(self, consent_level: str) -> bool:
        return consent_level in PRIVATE_NO_WRITE_LEVELS

    def _hash_content(self, content: str) -> str:
        """Create a secure hash of content for privacy protection."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _create_anonymized_hash(self, user_message: str, ai_response: str) -> str:
        """Create an anonymized representation for pattern analysis."""
        anonymized_user = self._anonymize_text(user_message)
        anonymized_response = self._anonymize_text(ai_response)
        combined = f"{anonymized_user}|{anonymized_response}"
        return hashlib.md5(combined.encode("utf-8")).hexdigest()

    def _anonymize_text(self, text: str) -> str:
        """Remove simple personal identifiers from text."""
        anonymized = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", text)
        anonymized = re.sub(r"\b\d{3}-\d{3}-\d{4}\b", "[PHONE]", anonymized)
        anonymized = re.sub(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", "[NAME]", anonymized)
        anonymized = re.sub(r"\b\d{1,5} [A-Za-z ]+ (Street|St|Avenue|Ave|Road|Rd|Drive|Dr)\b", "[ADDRESS]", anonymized)
        return anonymized

    def _extract_patterns(self, user_message: str, ai_response: str, ai_persona: str) -> Dict[str, Any]:
        """Extract patterns from conversation for collective learning."""
        return {
            "themes": self._identify_themes(user_message),
            "guidance_type": self._classify_guidance_type(ai_response),
            "persona_effectiveness": self._assess_persona_effectiveness(ai_persona, user_message),
            "emotional_tone": self._analyze_emotional_tone(user_message, ai_response),
            "transformation_indicators": self._identify_transformation_indicators(user_message, ai_response),
        }

    def _identify_themes(self, user_message: str) -> List[str]:
        themes = []
        theme_keywords = {
            "spiritual_growth": ["spiritual", "awakening", "consciousness", "enlightenment", "soul"],
            "relationships": ["relationship", "love", "partner", "family", "friend"],
            "career_purpose": ["career", "job", "purpose", "calling", "work"],
            "healing": ["healing", "trauma", "pain", "recovery", "therapy"],
            "creativity": ["creative", "art", "music", "writing", "expression"],
            "decision_making": ["decision", "choice", "confused", "uncertain", "direction"],
            "personal_growth": ["growth", "development", "improvement", "change", "transformation"],
            "meaning_purpose": ["meaning", "purpose", "why", "point", "significance"],
        }
        user_lower = user_message.lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                themes.append(theme)
        return themes

    def _classify_guidance_type(self, ai_response: str) -> str:
        response_lower = ai_response.lower()
        if any(word in response_lower for word in ["reflect", "consider", "explore", "examine"]):
            return "reflective"
        if any(word in response_lower for word in ["action", "step", "do", "try", "practice"]):
            return "actionable"
        if any(word in response_lower for word in ["perspective", "view", "see", "understand"]):
            return "perspective_shift"
        if any(word in response_lower for word in ["feel", "emotion", "heart", "compassion"]):
            return "emotional_support"
        return "informational"

    def _assess_persona_effectiveness(self, ai_persona: str, user_message: str) -> Dict[str, int]:
        user_lower = user_message.lower()
        steven_keywords = ["logic", "reason", "structure", "system", "chaos", "order", "transformation"]
        sarah_keywords = ["feel", "emotion", "heart", "healing", "relationship", "love", "gentle"]
        both_keywords = ["complex", "confused", "multiple", "perspective", "help", "guidance"]
        return {
            "steven_indicators": sum(1 for keyword in steven_keywords if keyword in user_lower),
            "sarah_indicators": sum(1 for keyword in sarah_keywords if keyword in user_lower),
            "both_indicators": sum(1 for keyword in both_keywords if keyword in user_lower),
        }

    def _analyze_emotional_tone(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        user_lower = user_message.lower()
        response_lower = ai_response.lower()
        positive_words = ["happy", "joy", "love", "grateful", "excited", "hopeful", "peaceful"]
        negative_words = ["sad", "angry", "frustrated", "worried", "anxious", "depressed", "lost"]
        user_positive = sum(1 for word in positive_words if word in user_lower)
        user_negative = sum(1 for word in negative_words if word in user_lower)
        response_supportive = sum(1 for word in ["understand", "support", "compassion", "gentle"] if word in response_lower)
        return {
            "user_tone": "positive" if user_positive > user_negative else "negative" if user_negative > 0 else "neutral",
            "response_supportiveness": response_supportive,
            "emotional_shift_potential": response_supportive,
        }

    def _identify_transformation_indicators(self, user_message: str, ai_response: str) -> List[str]:
        indicators = []
        user_lower = user_message.lower()
        response_lower = ai_response.lower()
        if any(word in user_lower for word in ["breakthrough", "realization", "understand", "clarity"]):
            indicators.append("breakthrough_moment")
        if any(word in user_lower for word in ["ready", "change", "grow", "transform"]):
            indicators.append("growth_readiness")
        if any(word in user_lower for word in ["stuck", "can't", "impossible", "hopeless"]):
            indicators.append("resistance_present")
        if any(word in response_lower for word in ["integrate", "embody", "practice", "apply"]):
            indicators.append("integration_guidance")
        return indicators

    def _assess_wisdom_contribution(self, conversation: ConversationEntry) -> Dict[str, Any]:
        if not conversation.extracted_patterns:
            return {}
        return {
            "novelty_score": self._calculate_novelty_score(conversation.extracted_patterns),
            "universality_score": self._calculate_universality_score(conversation.extracted_patterns),
            "transformation_potential": self._calculate_transformation_potential(conversation.extracted_patterns),
            "ethical_alignment": self._assess_ethical_alignment(conversation),
        }

    def _calculate_novelty_score(self, patterns: Dict[str, Any]) -> float:
        theme_count = len(patterns.get("themes", []))
        unique_indicators = len(set(patterns.get("transformation_indicators", [])))
        return min(1.0, (theme_count + unique_indicators) / 10.0)

    def _calculate_universality_score(self, patterns: Dict[str, Any]) -> float:
        universal_themes = ["personal_growth", "meaning_purpose", "relationships", "decision_making"]
        theme_overlap = len(set(patterns.get("themes", [])) & set(universal_themes))
        return min(1.0, theme_overlap / len(universal_themes))

    def _calculate_transformation_potential(self, patterns: Dict[str, Any]) -> float:
        transformation_indicators = patterns.get("transformation_indicators", [])
        positive_indicators = ["breakthrough_moment", "growth_readiness", "integration_guidance"]
        positive_count = len(set(transformation_indicators) & set(positive_indicators))
        return min(1.0, positive_count / len(positive_indicators))

    def _assess_ethical_alignment(self, conversation: ConversationEntry) -> float:
        ethical_indicators = [
            "sovereignty" in conversation.ai_response.lower(),
            "consent" in conversation.ai_response.lower(),
            "transparency" in conversation.ai_response.lower(),
            "service to life" in conversation.ai_response.lower(),
            not any(word in conversation.ai_response.lower() for word in ["manipulate", "control", "force"]),
        ]
        return sum(ethical_indicators) / len(ethical_indicators)

    def _store_conversation_db(self, conversation: ConversationEntry, user_hash: str, response_hash: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversations
            (id, session_id, timestamp, user_message_hash, ai_response_hash,
             ai_persona, ai_mode, user_consent_level, anonymized_hash,
             extracted_patterns, wisdom_contribution)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conversation.id,
                conversation.session_id,
                conversation.timestamp.isoformat(),
                user_hash,
                response_hash,
                conversation.ai_persona,
                conversation.ai_mode,
                conversation.user_consent_level,
                conversation.anonymized_hash,
                json.dumps(conversation.extracted_patterns) if conversation.extracted_patterns else None,
                json.dumps(conversation.wisdom_contribution) if conversation.wisdom_contribution else None,
            ),
        )
        conn.commit()
        conn.close()

    def _process_collective_learning(self, conversation: ConversationEntry) -> None:
        if not conversation.extracted_patterns:
            return
        self._update_wisdom_patterns(conversation.extracted_patterns)
        self._check_for_collective_insights()

    def _update_wisdom_patterns(self, patterns: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for theme in patterns.get("themes", []):
            cursor.execute("SELECT id, frequency FROM wisdom_patterns WHERE theme = ?", (theme,))
            result = cursor.fetchone()
            if result:
                pattern_id, _frequency = result
                cursor.execute(
                    """
                    UPDATE wisdom_patterns
                    SET frequency = frequency + 1, last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (pattern_id,),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO wisdom_patterns
                    (id, pattern_type, theme, frequency, effectiveness_score, anonymized_examples)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (str(uuid.uuid4()), "theme", theme, 1, 0.5, json.dumps([])),
                )
        conn.commit()
        conn.close()

    def _check_for_collective_insights(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT theme, frequency, effectiveness_score
            FROM wisdom_patterns
            WHERE frequency >= 5 AND effectiveness_score > 0.7
            """
        )
        high_value_patterns = cursor.fetchall()
        for theme, frequency, effectiveness in high_value_patterns:
            cursor.execute("SELECT id FROM collective_insights WHERE title LIKE ?", (f"%{theme}%",))
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO collective_insights
                    (id, title, description, supporting_patterns, confidence_score, impact_potential)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        f"Collective Wisdom: {theme.replace('_', ' ').title()}",
                        f"Based on {frequency} conversations, this theme shows high transformation potential.",
                        json.dumps([theme]),
                        effectiveness,
                        "community",
                    ),
                )
        conn.commit()
        conn.close()


if __name__ == "__main__":
    memory_system = MemoryIntegrationSystem()
    session_id = "test_session_001"
    receipt_id = memory_system.update_user_consent(
        session_id=session_id,
        consent_level="collective",
        collective_learning_enabled=True,
    )
    print(f"Consent receipt: {receipt_id}")
    conv_id = memory_system.store_conversation(
        session_id=session_id,
        user_message="I'm feeling lost in my spiritual journey and need direction.",
        ai_response="Your path can begin with one clear, consensual step.",
        ai_persona="sarah",
        ai_mode="Gentle Mirror",
        user_consent_level="collective",
    )
    print(f"Stored conversation: {conv_id}")
    print(json.dumps(memory_system.get_network_statistics(), indent=2))
