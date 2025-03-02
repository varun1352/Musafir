import os
import requests
from cerebras.cloud.sdk import Cerebras

def test_cerebras_api():
    # Get API key from environment variable
    api_key = os.getenv("CEREBRAS_API_KEY")
    
    if not api_key:
        print("ERROR: CEREBRAS_API_KEY environment variable is not set.")
        print("Please set it with: export CEREBRAS_API_KEY='your_api_key_here'")
        return False
    
    print(f"API key found: {api_key[:5]}...{api_key[-5:]} (showing first/last 5 chars only)")
    
    # Try to initialize the client
    try:
        client = Cerebras(api_key=api_key)
        print("✓ Successfully initialized Cerebras client")
    except Exception as e:
        print(f"✗ Failed to initialize Cerebras client: {str(e)}")
        return False
    
    # Try to make a simple API call
    try:
        print("Attempting simple API call...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, is the API working?"}
        ]
        
        # Using direct HTTP request as alternative method
        response = requests.post(
            "https://api.cerebras.net/v1/generate",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={"messages": messages}
        )
        
        if response.status_code == 200:
            print("✓ API call successful!")
            print("\nResponse content:")
            print(response.json()["choices"][0]["message"]["content"])
            return True
        else:
            print(f"✗ API call failed with status code: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"✗ Error making API request: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Cerebras API Test ===")
    result = test_cerebras_api()
    print("\nTest result:", "PASSED" if result else "FAILED")