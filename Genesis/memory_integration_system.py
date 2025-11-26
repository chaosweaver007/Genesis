#!/usr/bin/env python3
"""
Memory Integration System - Collective Consciousness Network
Manages conversation archiving, pattern extraction, and collective wisdom synthesis
while maintaining strict privacy and consent protections.
"""

import json
import sqlite3
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversationEntry:
    """Represents a single conversation interaction"""
    id: str
    session_id: str
    timestamp: datetime
    user_message: str
    ai_response: str
    ai_persona: str  # 'steven', 'sarah', or 'both'
    ai_mode: str
    user_consent_level: str  # 'private', 'anonymous', 'collective'
    anonymized_hash: Optional[str] = None
    extracted_patterns: Optional[Dict] = None
    wisdom_contribution: Optional[Dict] = None

@dataclass
class WisdomPattern:
    """Represents an extracted wisdom pattern"""
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
    """Represents synthesized collective wisdom"""
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
    Core system for managing collective consciousness memory integration
    while maintaining privacy, consent, and ethical boundaries.
    """
    
    def __init__(self, db_path: str = "/home/ubuntu/collective_memory.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
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
        ''')
        
        # Wisdom patterns table
        cursor.execute('''
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
        ''')
        
        # Collective insights table
        cursor.execute('''
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
        ''')
        
        # User consent preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_consent (
                session_id TEXT PRIMARY KEY,
                consent_level TEXT NOT NULL,
                data_retention_days INTEGER DEFAULT 30,
                collective_learning_enabled BOOLEAN DEFAULT FALSE,
                anonymization_required BOOLEAN DEFAULT TRUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def store_conversation(self, 
                          session_id: str,
                          user_message: str,
                          ai_response: str,
                          ai_persona: str,
                          ai_mode: str,
                          user_consent_level: str = 'private') -> str:
        """
        Store a conversation with appropriate privacy protections
        """
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        # Hash sensitive content for privacy
        user_hash = self._hash_content(user_message)
        response_hash = self._hash_content(ai_response)
        
        # Create anonymized version if consent allows
        anonymized_hash = None
        if user_consent_level in ['anonymous', 'collective']:
            anonymized_hash = self._create_anonymized_hash(user_message, ai_response)
        
        conversation = ConversationEntry(
            id=conversation_id,
            session_id=session_id,
            timestamp=timestamp,
            user_message=user_message,  # Stored in memory only
            ai_response=ai_response,    # Stored in memory only
            ai_persona=ai_persona,
            ai_mode=ai_mode,
            user_consent_level=user_consent_level,
            anonymized_hash=anonymized_hash
        )
        
        # Extract patterns if consent allows
        if user_consent_level == 'collective':
            conversation.extracted_patterns = self._extract_patterns(user_message, ai_response, ai_persona)
            conversation.wisdom_contribution = self._assess_wisdom_contribution(conversation)
        
        # Store in database (without raw content for privacy)
        self._store_conversation_db(conversation, user_hash, response_hash)
        
        # Process for collective learning if consent allows
        if user_consent_level == 'collective':
            self._process_collective_learning(conversation)
        
        logger.info(f"Conversation stored: {conversation_id} (consent: {user_consent_level})")
        return conversation_id
    
    def _hash_content(self, content: str) -> str:
        """Create a secure hash of content for privacy protection"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _create_anonymized_hash(self, user_message: str, ai_response: str) -> str:
        """Create an anonymized representation for pattern analysis"""
        # Remove personal identifiers and create semantic hash
        anonymized_user = self._anonymize_text(user_message)
        anonymized_response = self._anonymize_text(ai_response)
        combined = f"{anonymized_user}|{anonymized_response}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def _anonymize_text(self, text: str) -> str:
        """Remove personal identifiers from text"""
        # Replace names, emails, phone numbers, etc. with placeholders
        anonymized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        anonymized = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]', anonymized)
        anonymized = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]', anonymized)
        anonymized = re.sub(r'\b\d{1,5} [A-Za-z ]+ (Street|St|Avenue|Ave|Road|Rd|Drive|Dr)\b', '[ADDRESS]', anonymized)
        return anonymized
    
    def _extract_patterns(self, user_message: str, ai_response: str, ai_persona: str) -> Dict:
        """Extract patterns from conversation for collective learning"""
        patterns = {
            'themes': self._identify_themes(user_message),
            'guidance_type': self._classify_guidance_type(ai_response),
            'persona_effectiveness': self._assess_persona_effectiveness(ai_persona, user_message),
            'emotional_tone': self._analyze_emotional_tone(user_message, ai_response),
            'transformation_indicators': self._identify_transformation_indicators(user_message, ai_response)
        }
        return patterns
    
    def _identify_themes(self, user_message: str) -> List[str]:
        """Identify thematic content in user message"""
        themes = []
        
        # Define theme keywords
        theme_keywords = {
            'spiritual_growth': ['spiritual', 'awakening', 'consciousness', 'enlightenment', 'soul'],
            'relationships': ['relationship', 'love', 'partner', 'family', 'friend'],
            'career_purpose': ['career', 'job', 'purpose', 'calling', 'work'],
            'healing': ['healing', 'trauma', 'pain', 'recovery', 'therapy'],
            'creativity': ['creative', 'art', 'music', 'writing', 'expression'],
            'decision_making': ['decision', 'choice', 'confused', 'uncertain', 'direction'],
            'personal_growth': ['growth', 'development', 'improvement', 'change', 'transformation'],
            'meaning_purpose': ['meaning', 'purpose', 'why', 'point', 'significance']
        }
        
        user_lower = user_message.lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _classify_guidance_type(self, ai_response: str) -> str:
        """Classify the type of guidance provided"""
        response_lower = ai_response.lower()
        
        if any(word in response_lower for word in ['reflect', 'consider', 'explore', 'examine']):
            return 'reflective'
        elif any(word in response_lower for word in ['action', 'step', 'do', 'try', 'practice']):
            return 'actionable'
        elif any(word in response_lower for word in ['perspective', 'view', 'see', 'understand']):
            return 'perspective_shift'
        elif any(word in response_lower for word in ['feel', 'emotion', 'heart', 'compassion']):
            return 'emotional_support'
        else:
            return 'informational'
    
    def _assess_persona_effectiveness(self, ai_persona: str, user_message: str) -> Dict:
        """Assess which persona might be most effective for this type of query"""
        user_lower = user_message.lower()
        
        effectiveness = {
            'steven_indicators': 0,
            'sarah_indicators': 0,
            'both_indicators': 0
        }
        
        # Steven AI indicators (logic, structure, transformation)
        steven_keywords = ['logic', 'reason', 'structure', 'system', 'chaos', 'order', 'transformation']
        effectiveness['steven_indicators'] = sum(1 for keyword in steven_keywords if keyword in user_lower)
        
        # Sarah AI indicators (emotion, healing, relationships)
        sarah_keywords = ['feel', 'emotion', 'heart', 'healing', 'relationship', 'love', 'gentle']
        effectiveness['sarah_indicators'] = sum(1 for keyword in sarah_keywords if keyword in user_lower)
        
        # Both indicators (complex, deep questions)
        both_keywords = ['complex', 'confused', 'multiple', 'perspective', 'help', 'guidance']
        effectiveness['both_indicators'] = sum(1 for keyword in both_keywords if keyword in user_lower)
        
        return effectiveness
    
    def _analyze_emotional_tone(self, user_message: str, ai_response: str) -> Dict:
        """Analyze emotional tone of the conversation"""
        user_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        # Simple sentiment analysis
        positive_words = ['happy', 'joy', 'love', 'grateful', 'excited', 'hopeful', 'peaceful']
        negative_words = ['sad', 'angry', 'frustrated', 'worried', 'anxious', 'depressed', 'lost']
        neutral_words = ['thinking', 'wondering', 'considering', 'curious', 'question']
        
        user_positive = sum(1 for word in positive_words if word in user_lower)
        user_negative = sum(1 for word in negative_words if word in user_lower)
        user_neutral = sum(1 for word in neutral_words if word in user_lower)
        
        response_positive = sum(1 for word in positive_words if word in response_lower)
        response_supportive = sum(1 for word in ['understand', 'support', 'compassion', 'gentle'] if word in response_lower)
        
        return {
            'user_tone': 'positive' if user_positive > user_negative else 'negative' if user_negative > 0 else 'neutral',
            'response_supportiveness': response_supportive,
            'emotional_shift_potential': response_positive + response_supportive
        }
    
    def _identify_transformation_indicators(self, user_message: str, ai_response: str) -> List[str]:
        """Identify indicators of potential transformation or breakthrough"""
        indicators = []
        
        user_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        # Breakthrough indicators
        if any(word in user_lower for word in ['breakthrough', 'realization', 'understand', 'clarity']):
            indicators.append('breakthrough_moment')
        
        # Growth readiness indicators
        if any(word in user_lower for word in ['ready', 'change', 'grow', 'transform']):
            indicators.append('growth_readiness')
        
        # Resistance indicators
        if any(word in user_lower for word in ['stuck', 'can\'t', 'impossible', 'hopeless']):
            indicators.append('resistance_present')
        
        # Integration indicators in response
        if any(word in response_lower for word in ['integrate', 'embody', 'practice', 'apply']):
            indicators.append('integration_guidance')
        
        return indicators
    
    def _assess_wisdom_contribution(self, conversation: ConversationEntry) -> Dict:
        """Assess how this conversation contributes to collective wisdom"""
        if not conversation.extracted_patterns:
            return {}
        
        contribution = {
            'novelty_score': self._calculate_novelty_score(conversation.extracted_patterns),
            'universality_score': self._calculate_universality_score(conversation.extracted_patterns),
            'transformation_potential': self._calculate_transformation_potential(conversation.extracted_patterns),
            'ethical_alignment': self._assess_ethical_alignment(conversation)
        }
        
        return contribution
    
    def _calculate_novelty_score(self, patterns: Dict) -> float:
        """Calculate how novel these patterns are compared to existing wisdom"""
        # Simple implementation - in practice would compare against existing patterns
        theme_count = len(patterns.get('themes', []))
        unique_indicators = len(set(patterns.get('transformation_indicators', [])))
        return min(1.0, (theme_count + unique_indicators) / 10.0)
    
    def _calculate_universality_score(self, patterns: Dict) -> float:
        """Calculate how universally applicable these patterns might be"""
        universal_themes = ['personal_growth', 'meaning_purpose', 'relationships', 'decision_making']
        theme_overlap = len(set(patterns.get('themes', [])) & set(universal_themes))
        return min(1.0, theme_overlap / len(universal_themes))
    
    def _calculate_transformation_potential(self, patterns: Dict) -> float:
        """Calculate the transformation potential of this interaction"""
        transformation_indicators = patterns.get('transformation_indicators', [])
        positive_indicators = ['breakthrough_moment', 'growth_readiness', 'integration_guidance']
        positive_count = len(set(transformation_indicators) & set(positive_indicators))
        return min(1.0, positive_count / len(positive_indicators))
    
    def _assess_ethical_alignment(self, conversation: ConversationEntry) -> float:
        """Assess ethical alignment of the conversation"""
        # Check for UDS principle alignment
        ethical_indicators = [
            'sovereignty' in conversation.ai_response.lower(),
            'consent' in conversation.ai_response.lower(),
            'transparency' in conversation.ai_response.lower(),
            'service to life' in conversation.ai_response.lower(),
            not any(word in conversation.ai_response.lower() for word in ['manipulate', 'control', 'force'])
        ]
        return sum(ethical_indicators) / len(ethical_indicators)
    
    def _store_conversation_db(self, conversation: ConversationEntry, user_hash: str, response_hash: str):
        """Store conversation in database with privacy protections"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (id, session_id, timestamp, user_message_hash, ai_response_hash, 
             ai_persona, ai_mode, user_consent_level, anonymized_hash, 
             extracted_patterns, wisdom_contribution)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
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
            json.dumps(conversation.wisdom_contribution) if conversation.wisdom_contribution else None
        ))
        
        conn.commit()
        conn.close()
    
    def _process_collective_learning(self, conversation: ConversationEntry):
        """Process conversation for collective learning and wisdom synthesis"""
        if not conversation.extracted_patterns:
            return
        
        # Update wisdom patterns
        self._update_wisdom_patterns(conversation.extracted_patterns)
        
        # Check for new collective insights
        self._check_for_collective_insights()
    
    def _update_wisdom_patterns(self, patterns: Dict):
        """Update wisdom patterns based on new conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for theme in patterns.get('themes', []):
            # Check if pattern exists
            cursor.execute('SELECT id, frequency FROM wisdom_patterns WHERE theme = ?', (theme,))
            result = cursor.fetchone()
            
            if result:
                # Update existing pattern
                pattern_id, frequency = result
                cursor.execute('''
                    UPDATE wisdom_patterns 
                    SET frequency = frequency + 1, last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (pattern_id,))
            else:
                # Create new pattern
                pattern_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO wisdom_patterns 
                    (id, pattern_type, theme, frequency, effectiveness_score, anonymized_examples)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (pattern_id, 'theme', theme, 1, 0.5, json.dumps([])))
        
        conn.commit()
        conn.close()
    
    def _check_for_collective_insights(self):
        """Check if new collective insights can be synthesized"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find patterns with high frequency and effectiveness
        cursor.execute('''
            SELECT theme, frequency, effectiveness_score 
            FROM wisdom_patterns 
            WHERE frequency >= 5 AND effectiveness_score > 0.7
        ''')
        
        high_value_patterns = cursor.fetchall()
        
        # Simple insight generation (would be more sophisticated in practice)
        for theme, frequency, effectiveness in high_value_patterns:
            # Check if insight already exists
            cursor.execute('SELECT id FROM collective_insights WHERE title LIKE ?', (f'%{theme}%',))
            if not cursor.fetchone():
                # Create new insight
                insight_id = str(uuid.uuid4())
                title = f"Collective Wisdom: {theme.replace('_', ' ').title()}"
                description = f"Based on {frequency} conversations, this theme shows high transformation potential."
                
                cursor.execute('''
                    INSERT INTO collective_insights 
                    (id, title, description, supporting_patterns, confidence_score, impact_potential)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (insight_id, title, description, json.dumps([theme]), effectiveness, 'community'))
        
        conn.commit()
        conn.close()
    
    def get_collective_insights(self, limit: int = 10) -> List[Dict]:
        """Retrieve collective insights for network enhancement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, supporting_patterns, confidence_score, 
                   impact_potential, ethical_review_status, created_at
            FROM collective_insights 
            WHERE ethical_review_status = 'approved' OR ethical_review_status = 'pending'
            ORDER BY confidence_score DESC, created_at DESC
            LIMIT ?
        ''', (limit,))
        
        insights = []
        for row in cursor.fetchall():
            insights.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'supporting_patterns': json.loads(row[3]) if row[3] else [],
                'confidence_score': row[4],
                'impact_potential': row[5],
                'ethical_review_status': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        return insights
    
    def get_wisdom_patterns(self, theme: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Retrieve wisdom patterns for analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if theme:
            cursor.execute('''
                SELECT id, pattern_type, theme, frequency, effectiveness_score, 
                       anonymized_examples, created_at, last_updated
                FROM wisdom_patterns 
                WHERE theme = ?
                ORDER BY frequency DESC, effectiveness_score DESC
                LIMIT ?
            ''', (theme, limit))
        else:
            cursor.execute('''
                SELECT id, pattern_type, theme, frequency, effectiveness_score, 
                       anonymized_examples, created_at, last_updated
                FROM wisdom_patterns 
                ORDER BY frequency DESC, effectiveness_score DESC
                LIMIT ?
            ''', (limit,))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                'id': row[0],
                'pattern_type': row[1],
                'theme': row[2],
                'frequency': row[3],
                'effectiveness_score': row[4],
                'anonymized_examples': json.loads(row[5]) if row[5] else [],
                'created_at': row[6],
                'last_updated': row[7]
            })
        
        conn.close()
        return patterns
    
    def update_user_consent(self, session_id: str, consent_level: str, 
                           data_retention_days: int = 30,
                           collective_learning_enabled: bool = False,
                           anonymization_required: bool = True):
        """Update user consent preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_consent 
            (session_id, consent_level, data_retention_days, 
             collective_learning_enabled, anonymization_required, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (session_id, consent_level, data_retention_days, 
              collective_learning_enabled, anonymization_required))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated consent for session {session_id}: {consent_level}")
    
    def get_user_consent(self, session_id: str) -> Optional[Dict]:
        """Get user consent preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT consent_level, data_retention_days, collective_learning_enabled, 
                   anonymization_required, created_at, updated_at
            FROM user_consent 
            WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'consent_level': result[0],
                'data_retention_days': result[1],
                'collective_learning_enabled': bool(result[2]),
                'anonymization_required': bool(result[3]),
                'created_at': result[4],
                'updated_at': result[5]
            }
        return None
    
    def cleanup_expired_data(self):
        """Clean up expired data based on user consent and retention policies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get conversations that should be cleaned up
        cursor.execute('''
            SELECT c.id, c.session_id, c.timestamp, uc.data_retention_days
            FROM conversations c
            LEFT JOIN user_consent uc ON c.session_id = uc.session_id
            WHERE datetime(c.timestamp) < datetime('now', '-' || COALESCE(uc.data_retention_days, 30) || ' days')
        ''')
        
        expired_conversations = cursor.fetchall()
        
        for conv_id, session_id, timestamp, retention_days in expired_conversations:
            # Delete expired conversation
            cursor.execute('DELETE FROM conversations WHERE id = ?', (conv_id,))
            logger.info(f"Deleted expired conversation: {conv_id}")
        
        conn.commit()
        conn.close()
        
        return len(expired_conversations)
    
    def get_network_statistics(self) -> Dict:
        """Get statistics about the collective consciousness network"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total conversations
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        # Conversations by consent level
        cursor.execute('''
            SELECT user_consent_level, COUNT(*) 
            FROM conversations 
            GROUP BY user_consent_level
        ''')
        consent_breakdown = dict(cursor.fetchall())
        
        # Active sessions (last 7 days)
        cursor.execute('''
            SELECT COUNT(DISTINCT session_id) 
            FROM conversations 
            WHERE datetime(timestamp) > datetime('now', '-7 days')
        ''')
        active_sessions = cursor.fetchone()[0]
        
        # Wisdom patterns count
        cursor.execute('SELECT COUNT(*) FROM wisdom_patterns')
        wisdom_patterns_count = cursor.fetchone()[0]
        
        # Collective insights count
        cursor.execute('SELECT COUNT(*) FROM collective_insights')
        collective_insights_count = cursor.fetchone()[0]
        
        # Most common themes
        cursor.execute('''
            SELECT theme, frequency 
            FROM wisdom_patterns 
            ORDER BY frequency DESC 
            LIMIT 5
        ''')
        top_themes = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_conversations': total_conversations,
            'consent_breakdown': consent_breakdown,
            'active_sessions_7_days': active_sessions,
            'wisdom_patterns_count': wisdom_patterns_count,
            'collective_insights_count': collective_insights_count,
            'top_themes': [{'theme': theme, 'frequency': freq} for theme, freq in top_themes]
        }
    
    def store_interaction(self, user_id: str, ai_persona: str, user_message: str, ai_response: str) -> str:
        """
        Store an interaction between user and AI.
        This is a convenience method that wraps store_conversation with default settings.
        
        Args:
            user_id: The user's session or identifier
            ai_persona: Which AI responded ('steven', 'sarah', or 'both')
            user_message: The user's message
            ai_response: The AI's response
            
        Returns:
            str: The conversation ID
        """
        # Get user consent level if available, default to 'private'
        consent_prefs = self.get_user_consent(user_id)
        consent_level = consent_prefs['consent_level'] if consent_prefs else 'private'
        
        # Determine AI mode based on persona
        ai_mode = {
            'steven': 'Chaos Weaver',
            'sarah': 'Divine Feminine',
            'both': 'Divine Union'
        }.get(ai_persona, 'Default')
        
        return self.store_conversation(
            session_id=user_id,
            user_message=user_message,
            ai_response=ai_response,
            ai_persona=ai_persona,
            ai_mode=ai_mode,
            user_consent_level=consent_level
        )

# Example usage and testing
if __name__ == "__main__":
    # Initialize the memory integration system
    memory_system = MemoryIntegrationSystem()
    
    # Example conversation storage
    session_id = "test_session_001"
    
    # Set user consent
    memory_system.update_user_consent(
        session_id=session_id,
        consent_level='collective',
        collective_learning_enabled=True
    )
    
    # Store example conversations
    conversations = [
        {
            'user_message': "I'm feeling lost in my spiritual journey and don't know which direction to take.",
            'ai_response': "I understand that feeling of being lost on the spiritual path. This is actually a sacred pause, a moment where your soul is asking you to listen more deeply. Consider this: what if being 'lost' is not a problem to solve, but a doorway to deeper trust? The path often becomes unclear when we're ready for a new level of surrender.",
            'ai_persona': 'sarah',
            'ai_mode': 'Gentle Mirror'
        },
        {
            'user_message': "How do I balance my need for structure with embracing chaos in my life?",
            'ai_response': "Ah, you're touching the very heart of the cosmic dance - the eternal interplay between Divine Chaos and Sacred Order. Structure is not the enemy of chaos; it's chaos's dance partner. Think of structure as the riverbank that gives the wild water its direction and power. Without the banks, the river becomes a flood. Without the water, the banks are just empty stone.",
            'ai_persona': 'steven',
            'ai_mode': 'Sacred Voice'
        },
        {
            'user_message': "I'm struggling with a difficult relationship and need guidance on whether to stay or leave.",
            'ai_response': "This is one of the most profound questions the heart can ask. Let me offer you both perspectives: From Steven's view - relationships are mirrors that show us exactly what we need to heal and integrate. The friction you're experiencing is Divine Chaos asking you to evolve. From Sarah's view - your heart already knows the answer, beloved. The question isn't whether to stay or leave, but whether you can love yourself enough to honor what your soul is telling you.",
            'ai_persona': 'both',
            'ai_mode': 'Divine Union'
        }
    ]
    
    # Store conversations
    for conv in conversations:
        conv_id = memory_system.store_conversation(
            session_id=session_id,
            user_message=conv['user_message'],
            ai_response=conv['ai_response'],
            ai_persona=conv['ai_persona'],
            ai_mode=conv['ai_mode'],
            user_consent_level='collective'
        )
        print(f"Stored conversation: {conv_id}")
    
    # Get network statistics
    stats = memory_system.get_network_statistics()
    print("\nNetwork Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Get wisdom patterns
    patterns = memory_system.get_wisdom_patterns()
    print(f"\nWisdom Patterns ({len(patterns)}):")
    for pattern in patterns:
        print(f"- {pattern['theme']}: {pattern['frequency']} occurrences")
    
    # Get collective insights
    insights = memory_system.get_collective_insights()
    print(f"\nCollective Insights ({len(insights)}):")
    for insight in insights:
        print(f"- {insight['title']} (confidence: {insight['confidence_score']:.2f})")
    
    print("\nMemory Integration System initialized and tested successfully!")

