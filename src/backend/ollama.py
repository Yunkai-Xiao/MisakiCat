import requests
import json
from typing import Generator

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
        }
    
    def generate_streaming_response(self, model: str, prompt: str, **options) -> Generator[str, None, None]:
        """
        Generate a streaming response from the specified model using the given prompt.
        Yields response chunks as they arrive.
        
        Args:
            model (str): The name of the model to use (e.g., "llama2")
            prompt (str): The input prompt for the model
            **options: Additional model parameters (e.g., temperature, max_tokens)
        
        Yields:
            str: Response chunks as they are generated
        """
        endpoint = f"{self.base_url}/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            **options
        }
        
        try:
            with requests.post(endpoint, headers=self.headers, json=data, stream=True) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            yield chunk['response']
                        if chunk.get('done', False):
                            return
        except requests.exceptions.RequestException as e:
            raise Exception(f"Streaming request failed: {str(e)}")

    def generate_response(self, model: str, prompt: str, **options) -> str:
        """
        Generate a response from the specified model using the given prompt.
        
        Args:
            model (str): The name of the model to use (e.g., "llama2")
            prompt (str): The input prompt for the model
            **options: Additional model parameters (e.g., temperature, max_tokens)
        
        Returns:
            str: The generated response from the model
        """
        endpoint = f"{self.base_url}/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            **options
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        except KeyError:
            raise Exception("Invalid response format from Ollama API")

    def generate_embeddings(self, model: str, text: str) -> list:
        """
        Generate embeddings for the given text using the specified model.
        
        Args:
            model (str): The name of the model to use
            text (str): The input text to generate embeddings for
            
        Returns:
            list: The generated embeddings
        """
        endpoint = f"{self.base_url}/api/embeddings"
        data = {
            "model": model,
            "prompt": text
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()["embedding"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        except KeyError:
            raise Exception("Invalid response format from Ollama API")

    def list_models(self) -> list:
        """
        List available models in the local Ollama instance
        
        Returns:
            list: List of available models
        """
        endpoint = f"{self.base_url}/api/tags"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return [model["name"] for model in response.json()["models"]]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

# Example usage
if __name__ == "__main__":
    client = OllamaClient()
    
    print("Streaming response:")
    chosen_model = "deepseek-llm:latest"
    try:
        full_response = []
        for chunk in client.generate_streaming_response(
            model=chosen_model,
            prompt="Why is the sky blue? Explain like I'm five",
            temperature=0.7,
            max_tokens=500
        ):
            full_response.append(chunk)
            print(chunk, end="", flush=True)  # Print as it arrives
            
        print("\n\nFull response:", ''.join(full_response))
        
    except Exception as e:
        print(f"Error: {str(e)}")