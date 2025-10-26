#!/usr/bin/env python3
"""
Test script to verify Gemini API integration using HTTP (same as app.py)
"""

import os
import requests

# Get Gemini API key from environment variable (NEVER hardcode it!)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

def test_gemini_api():
    """Test Gemini API response generation using HTTP (same method as app.py)"""
    print("🤖 Testing Google Gemini API Integration (HTTP)...\n")
    
    if not GEMINI_API_KEY:
        print("❌ ERROR: GEMINI_API_KEY environment variable is not set!")
        print("\n⚠️  Please set your API key:")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        print("\nOr create a .env file with:")
        print("   GEMINI_API_KEY=your-api-key-here")
        return
    
    try:
        # Show API info first
        print("📊 API Information:")
        print(f"  - Model: {GEMINI_MODEL}")
        print(f"  - API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
        print(f"  - Status: Checking...\n")
        
        # Test 1: Positive tone - Movie review
        print("=" * 70)
        print("📝 Test 1: Positive Movie Review")
        print("=" * 70)
        
        prompt1 = """You are filling out a form. Context: Movie feedback survey

Instructions:
- Answer positively and enthusiastically. Show satisfaction and approval.
- Keep responses natural and human-like
- Write 2-4 sentences
- Be specific and detailed
- Stay relevant to the question

Question: What did you think of the director's vision and cinematography?

Answer:"""
        
        response1 = call_gemini_api(prompt1)
        if response1:
            print(f"✅ Response:\n{response1}\n")
        else:
            print(f"❌ Failed to get response\n")
            return
        
        # Test 2: Negative tone - Product review
        print("=" * 70)
        print("📝 Test 2: Negative Product Review")
        print("=" * 70)
        
        prompt2 = """You are filling out a form. Context: Software product survey

Instructions:
- Answer with criticism and dissatisfaction. Point out issues.
- Keep responses natural and human-like
- Write 2-4 sentences
- Be specific and detailed
- Stay relevant to the question

Question: Describe your experience with the software interface.

Answer:"""
        
        response2 = call_gemini_api(prompt2)
        if response2:
            print(f"✅ Response:\n{response2}\n")
        else:
            print(f"❌ Failed to get response\n")
            return
        
        # Test 3: Neutral tone - General feedback
        print("=" * 70)
        print("📝 Test 3: Neutral Feedback")
        print("=" * 70)
        
        prompt3 = """You are filling out a form. Context: General feedback survey

Instructions:
- Answer objectively and balanced.
- Keep responses natural and human-like
- Write 2-4 sentences
- Be specific and detailed
- Stay relevant to the question

Question: What are your overall thoughts?

Answer:"""
        
        response3 = call_gemini_api(prompt3)
        if response3:
            print(f"✅ Response:\n{response3}\n")
        else:
            print(f"❌ Failed to get response\n")
            return
        
        print("=" * 70)
        print("🎉 SUCCESS! Google Gemini API is working perfectly!")
        print("=" * 70)
        print("\n✨ Your form filler is ready to generate intelligent responses!\n")
        
        # Show API info
        print("📊 API Summary:")
        print(f"  - Model: {GEMINI_MODEL}")
        print(f"  - API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
        print(f"  - Status: ✅ Active and working")
        print(f"  - Tests Passed: 3/3")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n⚠️  Please check:")
        print("1. API key is valid and has quota")
        print("2. Internet connection is working")
        print("3. API key has Gemini API enabled")
        print("4. Requests library is installed: pip install requests")

def call_gemini_api(prompt):
    """Call Gemini API via HTTP (same as app.py)"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "topK": 40,
                "maxOutputTokens": 220
            }
        }
        resp = requests.post(url, json=payload, timeout=30)
        
        if resp.status_code != 200:
            print(f"❌ API Error: Status {resp.status_code}")
            print(f"Response: {resp.text}")
            return None
            
        data = resp.json()
        
        # Extract text
        try:
            cands = data.get('candidates') or []
            for c in cands:
                content = c.get('content') or {}
                parts = content.get('parts') or []
                for p in parts:
                    t = p.get('text')
                    if t:
                        return t.strip()
        except Exception as e:
            print(f"❌ Error parsing response: {e}")
            return None
            
        return None
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

if __name__ == "__main__":
    test_gemini_api()
