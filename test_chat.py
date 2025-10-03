import requests
import json

# Test the chat endpoint
def test_chat():
    url = "http://localhost:8000/chat"
    
    # Test health-related question
    health_question = {
        "message": "What should I do if I have a headache?",
        "session_id": "test_session_001"
    }
    
    try:
        response = requests.post(url, json=health_question)
        print("Health Question Response:")
        print(json.dumps(response.json(), indent=2))
        print("\n" + "="*50 + "\n")
        
        # Test non-health question
        non_health_question = {
            "message": "What is 2 + 2?",
            "session_id": "test_session_001"
        }
        
        response = requests.post(url, json=non_health_question)
        print("Non-Health Question Response:")
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat()