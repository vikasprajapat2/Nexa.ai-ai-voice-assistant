"""
Nexa Custom AI Model
Self-training conversational AI that learns from user interactions
"""

import json
import os
import re
from collections import defaultdict
import random
from datetime import datetime

class NexaAI:
    def __init__(self, memory_file="nexa_memory.json", model_file="nexa_model.json"):
        self.memory_file = memory_file
        self.model_file = model_file
        self.model = self.load_model()
        self.conversation_history = []  # Track current conversation
        self.max_history = 10  # Remember last 10 exchanges
        
    def load_model(self):
        """Load the trained model from file"""
        if os.path.exists(self.model_file):
            with open(self.model_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "patterns": {},  # keyword -> list of responses
            "context": {},   # conversation context
            "intents": {},   # classified intents
            "vocabulary": [],  # known words (changed from set for JSON)
            "response_quality": {},  # track which responses work best
            "conversations": []  # multi-turn conversations
        }
    
    def save_model(self):
        """Save the trained model to file"""
        with open(self.model_file, 'w', encoding='utf-8') as f:
            json.dump(self.model, f, indent=2, ensure_ascii=False)
    
    def tokenize(self, text):
        """Break text into words"""
        text = re.sub(r'[^\w\s]', '', text.lower())
        return text.split()
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        tokens = self.tokenize(text)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but', 'it', 'this', 'that'}
        keywords = [word for word in tokens if word not in stop_words and len(word) > 2]
        return keywords
    
    def classify_intent(self, text):
        """Determine the intent of the user's message"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'namaste']):
            return 'greeting'
        elif any(word in text_lower for word in ['bye', 'goodbye', 'see you']):
            return 'farewell'
        elif any(word in text_lower for word in ['thank', 'thanks']):
            return 'gratitude'
        elif '?' in text or any(word in text_lower for word in ['what', 'when', 'where', 'who', 'why', 'how']):
            return 'question'
        elif any(word in text_lower for word in ['open', 'search', 'play', 'type']):
            return 'command'
        elif any(word in text_lower for word in ['tell me', 'explain', 'describe']):
            return 'information_request'
        else:
            return 'statement'
    
    def get_conversation_context(self):
        """Get recent conversation context"""
        if len(self.conversation_history) < 2:
            return None
        
        # Get last few exchanges
        recent = self.conversation_history[-3:]
        context = {
            "previous_topic": None,
            "previous_intent": None,
            "keywords": []
        }
        
        for exchange in recent:
            if "user" in exchange:
                keywords = self.extract_keywords(exchange["user"])
                context["keywords"].extend(keywords)
                context["previous_intent"] = self.classify_intent(exchange["user"])
        
        return context
    
    def is_follow_up_question(self, text):
        """Detect if this is a follow-up question"""
        follow_up_indicators = ['also', 'and', 'what about', 'how about', 'tell me more', 
                                'continue', 'go on', 'anything else', 'more', 'else']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in follow_up_indicators)
    
    def train(self, user_input, assistant_response):
        """Train the model on a conversation pair"""
        # Add to conversation history
        self.conversation_history.append({
            "user": user_input,
            "assistant": assistant_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        # Extract keywords
        keywords = self.extract_keywords(user_input)
        intent = self.classify_intent(user_input)
        
        # Add to vocabulary
        for word in keywords:
            if word not in self.model["vocabulary"]:
                self.model["vocabulary"].append(word)
        
        # Store pattern-response pairs
        for keyword in keywords:
            if keyword not in self.model["patterns"]:
                self.model["patterns"][keyword] = []
            
            response_entry = {
                "response": assistant_response,
                "context": intent,
                "count": 1,
                "last_used": datetime.now().isoformat()
            }
            
            existing = False
            for entry in self.model["patterns"][keyword]:
                if entry["response"] == assistant_response:
                    entry["count"] += 1
                    entry["last_used"] = datetime.now().isoformat()
                    existing = True
                    break
            
            if not existing:
                self.model["patterns"][keyword].append(response_entry)
        
        # Store intent patterns
        if intent not in self.model["intents"]:
            self.model["intents"][intent] = []
        
        self.model["intents"][intent].append({
            "input": user_input,
            "response": assistant_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Store multi-turn conversations
        if len(self.conversation_history) >= 2:
            if "conversations" not in self.model:
                self.model["conversations"] = []
            self.model["conversations"].append({
                "exchanges": self.conversation_history[-2:],
                "timestamp": datetime.now().isoformat()
            })
        
        self.save_model()
    
    def generate_response(self, user_input):
        """Generate a contextual response based on learned patterns and conversation history"""
        keywords = self.extract_keywords(user_input)
        intent = self.classify_intent(user_input)
        context = self.get_conversation_context()
        
        # IMPORTANT: Only respond if we have HIGH CONFIDENCE
        # This allows Gemini API to handle most questions
        MIN_CONFIDENCE_SCORE = 10  # Require at least score of 10
        
        # Check if this is a follow-up question
        if self.is_follow_up_question(user_input) and context:
            # Use context keywords as well
            keywords.extend(context["keywords"])
        
        # Find matching patterns with context awareness
        candidate_responses = []
        
        for keyword in keywords:
            if keyword in self.model["patterns"]:
                for entry in self.model["patterns"][keyword]:
                    score = entry["count"]
                    
                    # Boost score if intent matches
                    if entry["context"] == intent:
                        score *= 2
                    
                    # Boost score if it's a recent pattern
                    if entry["count"] > 5:
                        score *= 1.5
                    
                    candidate_responses.append((entry["response"], score))
        
        # Check for similar multi-turn conversations
        if len(self.conversation_history) > 0 and "conversations" in self.model:
            last_user_msg = self.conversation_history[-1].get("user", "") if self.conversation_history else ""
            
            for conv in self.model["conversations"]:
                if len(conv["exchanges"]) >= 2:
                    # Check if previous exchange is similar
                    prev_user = conv["exchanges"][0].get("user", "")
                    if self.calculate_similarity(last_user_msg, prev_user) > 0.5:
                        # Use the follow-up response
                        if len(conv["exchanges"]) > 1:
                            follow_up = conv["exchanges"][1].get("assistant", "")
                            candidate_responses.append((follow_up, 20))  # High score for conversation patterns
        
        # Only return response if we have HIGH CONFIDENCE
        if candidate_responses:
            candidate_responses.sort(key=lambda x: x[1], reverse=True)
            best_response, best_score = candidate_responses[0]
            
            # Only use this response if confidence is high enough
            if best_score >= MIN_CONFIDENCE_SCORE:
                return best_response
        
        # DON'T use intent-based responses for questions - let Gemini handle them
        # Only use for greetings, farewells, and gratitude
        if intent in ['greeting', 'farewell', 'gratitude']:
            if intent in self.model["intents"] and self.model["intents"][intent]:
                similar = random.choice(self.model["intents"][intent])
                return similar["response"]
        
        # Return None to let Gemini API handle the question
        return None
    
    def calculate_similarity(self, text1, text2):
        """Calculate simple similarity between two texts"""
        words1 = set(self.tokenize(text1))
        words2 = set(self.tokenize(text2))
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0
    
    def get_stats(self):
        """Get model statistics"""
        return {
            "vocabulary_size": len(self.model["vocabulary"]),
            "patterns_learned": len(self.model["patterns"]),
            "intents_known": len(self.model["intents"]),
            "total_training_examples": sum(len(v) for v in self.model["intents"].values()),
            "conversations_stored": len(self.model.get("conversations", [])),
            "current_conversation_length": len(self.conversation_history)
        }
    
    def export_knowledge(self):
        """Export learned knowledge in human-readable format"""
        knowledge = {
            "vocabulary": self.model["vocabulary"],
            "top_patterns": {},
            "intents": list(self.model["intents"].keys()),
            "conversation_examples": []
        }
        
        # Get top patterns
        for keyword, responses in self.model["patterns"].items():
            if responses:
                top_response = max(responses, key=lambda x: x["count"])
                knowledge["top_patterns"][keyword] = {
                    "response": top_response["response"],
                    "usage_count": top_response["count"]
                }
        
        # Get conversation examples
        if "conversations" in self.model:
            knowledge["conversation_examples"] = self.model["conversations"][-5:]  # Last 5
        
        return knowledge
    
    def reset_conversation(self):
        """Reset the current conversation context"""
        self.conversation_history = []


# Example usage
if __name__ == "__main__":
    nexa = NexaAI()
    
    # Simulate a conversation
    nexa.train("Hello Nexa", "Hello! How can I help you?")
    nexa.train("What's the weather like?", "I don't have access to weather data, but I can help you search for it online!")
    nexa.train("Tell me more", "I can open a weather website for you, or search Google for your local weather. What would you prefer?")
    
    # Test conversation context
    print(nexa.generate_response("Hi there"))  # Should use greeting pattern
    print(nexa.generate_response("Tell me more"))  # Should recognize follow-up
    
    print(nexa.get_stats())
