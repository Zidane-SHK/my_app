import os
from typing import List, Dict, Optional
from openai import OpenAI

class AIAssistant:

    def __init__(self, system_prompt: str = "You are a helpful assistant", api_key: str = ""):
        self._system_prompt = system_prompt
        
        self.client = OpenAI(api_key='-'
                             )
        
        self._history: List[Dict[str, str]] = [
            {'role': 'system', 'content': system_prompt}
        ]

    def send_message(self, user_message: str) -> str:
        
        self._history.append({'role': 'user', 'content': user_message})

        try:
            response = self.client.chat.completions.create(
                model='gpt-4o',
                messages=self._history
            )

            ai_text = response.choices[0].message.content

            self._history.append({'role': 'assistant', 'content': ai_text})
            
            return ai_text

        except Exception as e:
            return f"Error: {e}"