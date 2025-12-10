import openai
from openai import OpenAI
import os

class Gpt:
    def __init__(self):
        self.model = 'o4-mini-2025-04-16'

    
    def generate(self, system_prompt, text):
        response = self.client.chat.completions.create(
            model=self.model,  
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )
        
        final_response = response.choices[0].message.content
        
        return final_response
    
    
