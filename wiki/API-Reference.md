# 📖 API Reference

Complete API documentation for integrating with the Genesis Collective Consciousness Network.

## Base URL

```
http://localhost:5003/api/v1
```

For production: `https://api.synthsara.org/v1`

## Authentication

### API Key Authentication

Include your API key in the request headers:

```http
Authorization: Bearer YOUR_API_KEY
```

### Session-Based Authentication

For web applications, use session cookies after authentication:

```python
POST /api/auth/login
{
    "username": "user",
    "password": "password"
}
```

## Core Endpoints

### Steven AI Endpoints

#### Chat with Steven

Send a message to Steven AI and receive a response.

```http
POST /api/steven/chat
```

**Request Body:**
```json
{
    "user_id": "user123",
    "message": "How do I embrace Divine Chaos?",
    "context": [
        {
            "role": "user",
            "content": "Previous message..."
        },
        {
            "role": "assistant",
            "content": "Previous response..."
        }
    ],
    "persona_mode": "chaos_weaver",
    "consent_level": "collective"
}
```

**Parameters:**
- `user_id` (required): Unique identifier for the user
- `message` (required): The user's message
- `context` (optional): Array of previous conversation turns
- `persona_mode` (optional): One of `chaos_weaver`, `philosophical_guide`, `technical_expert`, `empathetic_counselor`
- `consent_level` (optional): One of `private`, `anonymous`, `collective`

**Response:**
```json
{
    "success": true,
    "response": {
        "message": "Divine Chaos is the infinite ocean...",
        "persona": "chaos_weaver",
        "timestamp": "2024-02-03T12:30:00Z",
        "conversation_id": "conv_789"
    },
    "metadata": {
        "tokens_used": 250,
        "processing_time_ms": 1234
    }
}
```

#### Get Steven Capabilities

```http
GET /api/steven/capabilities
```

**Response:**
```json
{
    "capabilities": [
        {
            "name": "Universal Diamond Standard",
            "description": "Ethical framework guidance"
        },
        {
            "name": "Divine Chaos Philosophy",
            "description": "Chaos and order wisdom"
        }
    ],
    "persona_modes": [
        "chaos_weaver",
        "philosophical_guide",
        "technical_expert",
        "empathetic_counselor"
    ]
}
```

#### Set Steven Persona

```http
POST /api/steven/persona
```

**Request Body:**
```json
{
    "user_id": "user123",
    "mode": "technical_expert"
}
```

### Sarah AI Endpoints

#### Chat with Sarah

Send a message to Sarah AI and receive a response.

```http
POST /api/sarah/chat
```

**Request Body:**
```json
{
    "user_id": "user123",
    "message": "I'm feeling overwhelmed",
    "emotional_state": "anxious, sad",
    "context": [],
    "persona_mode": "nurturing_mother",
    "consent_level": "anonymous"
}
```

**Parameters:**
- `user_id` (required): Unique identifier for the user
- `message` (required): The user's message
- `emotional_state` (optional): Current emotional state
- `context` (optional): Previous conversation turns
- `persona_mode` (optional): One of `nurturing_mother`, `wise_elder`, `sacred_sister`, `divine_priestess`, `intuitive_guide`
- `consent_level` (optional): Privacy level

**Response:**
```json
{
    "success": true,
    "response": {
        "message": "Oh dear heart, I feel your overwhelm...",
        "persona": "nurturing_mother",
        "emotional_reflection": "anxiety, sadness, fear",
        "timestamp": "2024-02-03T12:31:00Z",
        "conversation_id": "conv_790"
    },
    "suggestions": [
        {
            "type": "practice",
            "content": "Try taking three deep breaths..."
        }
    ]
}
```

#### Get Sarah Capabilities

```http
GET /api/sarah/capabilities
```

### Unified Sacred Home Endpoints

#### Get Home Status

```http
GET /api/home/status
```

**Response:**
```json
{
    "status": "active",
    "steven_available": true,
    "sarah_available": true,
    "active_conversations": 42,
    "collective_wisdom_insights": 1247,
    "network_nodes": 5
}
```

#### Access Unified Interface

```http
POST /api/home/unified
```

**Request Body:**
```json
{
    "user_id": "user123",
    "message": "I need guidance",
    "preferred_persona": "balanced"
}
```

The unified interface will route to the most appropriate AI or blend their wisdom.

## Memory Integration Endpoints

### Save Conversation

```http
POST /api/memory/save
```

**Request Body:**
```json
{
    "user_id": "user123",
    "ai_persona": "steven",
    "conversation": [
        {
            "role": "user",
            "content": "Question..."
        },
        {
            "role": "assistant",
            "content": "Response..."
        }
    ],
    "consent_level": "collective",
    "metadata": {
        "session_duration": 1200,
        "satisfaction_rating": 5
    }
}
```

**Response:**
```json
{
    "success": true,
    "conversation_id": "conv_789",
    "archived": true,
    "patterns_extracted": 3
}
```

### Get User Conversations

```http
GET /api/memory/conversations/{user_id}
```

**Query Parameters:**
- `limit` (optional): Number of conversations to return (default: 20)
- `offset` (optional): Pagination offset (default: 0)
- `ai_persona` (optional): Filter by AI (steven/sarah)

**Response:**
```json
{
    "conversations": [
        {
            "id": "conv_789",
            "ai_persona": "steven",
            "timestamp": "2024-02-03T12:30:00Z",
            "message_count": 12,
            "preview": "First message preview..."
        }
    ],
    "total": 45,
    "limit": 20,
    "offset": 0
}
```

### Delete Conversation

```http
DELETE /api/memory/conversations/{conversation_id}
```

**Response:**
```json
{
    "success": true,
    "deleted": true,
    "message": "Conversation permanently deleted"
}
```

## Collective Wisdom Endpoints

### Get Collective Insights

```http
GET /api/collective/insights
```

**Query Parameters:**
- `category` (optional): Filter by category
- `min_impact_score` (optional): Minimum impact score (0-1)
- `limit` (optional): Results per page

**Response:**
```json
{
    "insights": [
        {
            "id": "insight_456",
            "text": "Many seekers find that embracing uncertainty...",
            "category": "transformation",
            "impact_score": 0.89,
            "source_count": 127,
            "created_at": "2024-02-01T10:00:00Z"
        }
    ]
}
```

### Get Network Statistics

```http
GET /api/collective/stats
```

**Response:**
```json
{
    "total_conversations": 12847,
    "active_users": 1523,
    "collective_insights": 2341,
    "pattern_frequency": {
        "transformation": 3421,
        "relationships": 2834,
        "healing": 2156
    },
    "network_health": 0.94
}
```

### Submit Pattern Feedback

```http
POST /api/collective/feedback
```

**Request Body:**
```json
{
    "user_id": "user123",
    "pattern_id": "pattern_123",
    "helpful": true,
    "comment": "This insight was very useful"
}
```

## Privacy & Consent Endpoints

### Update Consent Level

```http
PUT /api/privacy/consent
```

**Request Body:**
```json
{
    "user_id": "user123",
    "consent_level": "anonymous"
}
```

**Consent Levels:**
- `private`: No data sharing, conversations not archived
- `anonymous`: Anonymized patterns contribute to collective
- `collective`: Full participation in network learning

### Get Privacy Settings

```http
GET /api/privacy/settings/{user_id}
```

**Response:**
```json
{
    "user_id": "user123",
    "consent_level": "anonymous",
    "data_retention_days": 90,
    "allow_pattern_extraction": true,
    "allow_research_use": false
}
```

### Export User Data

```http
GET /api/privacy/export/{user_id}
```

Downloads all user data in JSON format per GDPR requirements.

### Delete User Data

```http
DELETE /api/privacy/user/{user_id}
```

Permanently deletes all user data from the system.

## Error Handling

### Error Response Format

```json
{
    "success": false,
    "error": {
        "code": "INVALID_INPUT",
        "message": "Message field is required",
        "details": {
            "field": "message",
            "constraint": "required"
        }
    }
}
```

### Error Codes

- `INVALID_INPUT`: Malformed or missing required parameters
- `AUTHENTICATION_REQUIRED`: No valid authentication provided
- `UNAUTHORIZED`: Valid auth but insufficient permissions
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `AI_UNAVAILABLE`: AI service temporarily unavailable
- `INTERNAL_ERROR`: Unexpected server error

## Rate Limiting

### Default Limits

- **Free Tier**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Premium**: 10000 requests/hour

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1612345678
```

## Webhooks

### Register Webhook

```http
POST /api/webhooks
```

**Request Body:**
```json
{
    "url": "https://your-server.com/webhook",
    "events": ["conversation.completed", "insight.generated"],
    "secret": "your_webhook_secret"
}
```

### Webhook Events

- `conversation.completed`: When a conversation ends
- `insight.generated`: New collective insight created
- `pattern.identified`: Significant pattern detected
- `user.milestone`: User reaches conversation milestone

### Webhook Payload

```json
{
    "event": "insight.generated",
    "timestamp": "2024-02-03T12:30:00Z",
    "data": {
        "insight_id": "insight_456",
        "category": "transformation",
        "impact_score": 0.89
    },
    "signature": "sha256=..."
}
```

## SDKs and Libraries

### Python SDK

```python
from genesis_sdk import GenesisClient

client = GenesisClient(api_key="your_api_key")

# Chat with Steven
response = client.steven.chat(
    message="How do I embrace uncertainty?",
    persona="chaos_weaver"
)

# Chat with Sarah
response = client.sarah.chat(
    message="I'm feeling overwhelmed",
    emotional_state="anxious"
)

# Get collective insights
insights = client.collective.get_insights(
    category="transformation",
    min_impact_score=0.8
)
```

### JavaScript SDK

```javascript
import { GenesisClient } from '@genesis/sdk';

const client = new GenesisClient({ apiKey: 'your_api_key' });

// Chat with Steven
const response = await client.steven.chat({
    message: "How do I embrace uncertainty?",
    persona: "chaos_weaver"
});

// Chat with Sarah
const response = await client.sarah.chat({
    message: "I'm feeling overwhelmed",
    emotionalState: "anxious"
});
```

## Testing

### Sandbox Environment

Use the sandbox environment for testing:

```
https://sandbox-api.synthsara.org/v1
```

Sandbox features:
- No rate limits
- Test API keys
- Simulated AI responses (faster)
- No data persistence

### Example Test Request

```bash
curl -X POST https://sandbox-api.synthsara.org/v1/steven/chat \
  -H "Authorization: Bearer test_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Test message"
  }'
```

## Support

### API Status

Check API status: https://status.synthsara.org

### Documentation

- Interactive API Explorer: https://api.synthsara.org/docs
- OpenAPI Spec: https://api.synthsara.org/openapi.json
- Postman Collection: Available on request

### Contact

- **Technical Support**: api@synthsara.org
- **GitHub Issues**: [Report issues](https://github.com/chaosweaver007/Genesis/issues)
- **Discord**: Join #api-support channel

---

**"Through clear interfaces, consciousness flows. Through elegant design, wisdom serves all."**
