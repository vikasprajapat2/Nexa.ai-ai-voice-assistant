# Nexa AI - Learning System

## 🧠 Self-Learning Feature

Nexa now has a **self-learning system** that improves over time!

### How It Works:

1. **Conversation Storage**: Every conversation is saved to `nexa_memory.json`
2. **Pattern Recognition**: Nexa learns common questions and their best answers
3. **Memory Recall**: When you ask similar questions, Nexa remembers past responses
4. **Daily Training**: The more you use Nexa, the smarter it becomes!

### What Gets Learned:

- ✅ Common questions you ask
- ✅ Your preferred responses
- ✅ Patterns in your conversations
- ✅ Frequently used commands

### Memory File:

All learning data is stored in: `nexa_memory.json`

**Structure:**
```json
{
  "conversations": [
    {
      "timestamp": "2025-11-25T09:30:00",
      "user": "What time is it?",
      "assistant": "The current time is 9:30 AM."
    }
  ],
  "learned_responses": {
    "time": [
      {
        "question": "What time is it?",
        "answer": "The current time is 9:30 AM.",
        "count": 5
      }
    ]
  }
}
```

### View Learning Stats:

Visit: `http://localhost:5000/api/stats`

This shows:
- Total conversations
- Number of learned patterns
- Last conversation

### Privacy:

- All data is stored **locally** on your computer
- Nothing is sent to external servers
- You can delete `nexa_memory.json` anytime to reset memory

### Benefits:

1. **Faster Responses**: Nexa recalls answers from memory
2. **Personalized**: Learns your preferences over time
3. **Smarter**: Gets better at understanding your questions
4. **Offline Capable**: Uses learned responses even without internet

---

**Note**: The memory file is automatically created when you first use Nexa. It grows over time but is capped at 1000 conversations to keep it manageable.
