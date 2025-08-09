# memory_manager.py (ENHANCED VERSION)
import json
import os
from datetime import datetime

class SimpleMemoryManager:
    def __init__(self, user_id="demo_user"):
        self.user_id = user_id
        self.memory_file = f"memories_{user_id}.json"
        self.conversations = self.load_memories()
        print(f"Memory manager initialized for user: {user_id}")
    
    def store_emotion(self, emotion_data, context=""):
        """Store emotional data in memory"""
        try:
            memory_entry = {
                'id': len(self.conversations) + 1,
                'timestamp': emotion_data.get('timestamp', datetime.now().isoformat()),
                'emotion_scores': emotion_data,
                'context': context,
                'user_input': context,  # Store user input for easier access
                'primary_emotion': emotion_data.get('primary_emotion', 'neutral'),
                'stress_level': emotion_data.get('stress_level', 5),
                'emotion_intensity': emotion_data.get('emotion_intensity', 0.5),
                'risk_assessment': emotion_data.get('risk_assessment', 'low')
            }
            
            self.conversations.append(memory_entry)
            self.save_memories()
            print(f"Stored memory #{memory_entry['id']} - {emotion_data.get('primary_emotion', 'neutral')} (stress: {emotion_data.get('stress_level', 5)}/10)")
            
        except Exception as e:
            print(f"Error storing memory: {e}")
    
    def find_similar_emotions(self, current_intensity, limit=3):
        """Find similar emotional states from past conversations"""
        similar = []
        for memory in self.conversations:
            stored_intensity = memory.get('emotion_intensity', memory.get('emotion_scores', {}).get('emotion_intensity', 0.5))
            if abs(stored_intensity - current_intensity) < 0.3:
                similar.append(memory)
        
        return sorted(similar, key=lambda x: abs(x.get('emotion_intensity', 0.5) - current_intensity))[:limit]
    
    def get_recent_trend(self, days=7):
        """Get emotional trend over recent days"""
        recent_memories = self.conversations[-days:] if len(self.conversations) >= days else self.conversations
        if not recent_memories:
            return "neutral"
        
        avg_compound = sum(mem.get('stress_level', 5) for mem in recent_memories) / len(recent_memories)
        
        if avg_compound > 7:
            return "high_stress"
        elif avg_compound > 5:
            return "moderate_stress"
        elif avg_compound < 3:
            return "low_stress"
        else:
            return "stable"
    
    def save_memories(self):
        """Save memories to JSON file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.conversations, f, indent=2)
        except Exception as e:
            print(f"Error saving memories: {e}")
    
    def load_memories(self):
        """Load memories from JSON file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    print(f"Loaded {len(data)} previous conversations")
                    return data
            except Exception as e:
                print(f"Error loading memories: {e}")
                return []
        return []

if __name__ == "__main__":
    memory = SimpleMemoryManager("test")
    print(f"Loaded {len(memory.conversations)} previous conversations")
