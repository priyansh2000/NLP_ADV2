#!/usr/bin/env python3
"""
Test script for the RAG API
"""
import requests
import json
import os

# Test the API endpoints
def test_api():
    base_url = "http://localhost:8003"
    
    print("🧪 Testing RAG API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test query endpoint
    try:
        query_data = {
            "query": "What does Caesar say about the Ides of March?",
            "max_results": 3
        }
        
        response = requests.post(
            f"{base_url}/query", 
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Query test: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Query: {query_data['query']}")
            print(f"   Answer: {result.get('answer', 'No answer')[:200]}...")
            print(f"   Sources: {len(result.get('sources', []))} chunks retrieved")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Query test failed: {e}")

if __name__ == "__main__":
    # Set the Google API key from environment
    os.environ["GOOGLE_API_KEY"] = "AIzaSyAEfEs0RuZoNYLqcIK7YH3FcMsm0AS_e70"
    test_api()