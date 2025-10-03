# Bio Band AI Health Assistant Documentation

**Base URL:** `https://bio-band-backend.vercel.app`

---

## 🤖 AI Chat Endpoints

### 1. AI Health Chat
```http
POST /chat/
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "I have a headache, what should I do?",
  "session_id": "user123"
}
```

**Response:**
```json
{
  "success": true,
  "response": "For a headache, try these simple steps: 1) Drink water - you might be dehydrated. 2) Rest in a quiet, dark room. 3) Apply a cold or warm compress to your head. 4) Take a pain reliever like paracetamol if needed. If headaches happen often or are very severe, please see a doctor.",
  "session_id": "user123",
  "timestamp": "2025-10-02T16:00:00"
}
```

### 2. Get Chat History
```http
GET /chat/{session_id}
```

**Example:**
```http
GET /chat/user123
```

**Response:**
```json
{
  "success": true,
  "session_id": "user123",
  "history": [
    {
      "role": "user",
      "message": "I have a headache",
      "timestamp": "2025-10-02T16:00:00"
    },
    {
      "role": "assistant", 
      "message": "For a headache, try drinking water and resting...",
      "timestamp": "2025-10-02T16:00:05"
    }
  ],
  "message_count": 2
}
```

---

## 🧪 Test AI Chat

### Health Questions (Will Answer):
```bash
curl -X POST https://bio-band-backend.vercel.app/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a fever, what should I do?", "session_id": "test123"}'
```

```bash
curl -X POST https://bio-band-backend.vercel.app/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How can I lower my blood pressure?", "session_id": "test123"}'
```

### Non-Health Questions (Will Reject):
```bash
curl -X POST https://bio-band-backend.vercel.app/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2+2?", "session_id": "test123"}'
```

### Get Chat History:
```bash
curl https://bio-band-backend.vercel.app/chat/test123
```

---

## 📊 Database Storage

All chat messages are stored in Turso database:

```sql
-- Check chat messages
SELECT * FROM chat_messages ORDER BY timestamp DESC;

-- Get specific session
SELECT * FROM chat_messages WHERE session_id = 'user123' ORDER BY timestamp ASC;

-- Count total messages
SELECT COUNT(*) FROM chat_messages;
```

---

## 🎯 AI Features

✅ **Health-Focused**: Only answers health-related questions
✅ **Simple Language**: Uses easy-to-understand words
✅ **Persistent Storage**: All chats saved in Turso database
✅ **Session Management**: Track conversations by session_id
✅ **Powered by Gemini**: Google's advanced AI model