import requests
import json
from django.conf import settings

class PromptGeneratorService:
    """프롬프트 생성 서비스"""
    
    def generate_prompt(self, data):
        """
        사용자 입력에 기반한 프롬프트 생성
        """
        language = data['language']
        framework = data['framework']
        features = data['features']
        file_format = data['file_format']
        
        prompt = f"""당신은 초보 개발자를 돕는 도우미입니다. 
            다음 조건에 맞는 설정 파일을 생성해주세요:

            프로그래밍 언어: {language}
            프레임워크: {framework}
            필요한 기능:
        """
        
        for feature in features:
            prompt += f"- {feature}\n"
            
        prompt += f"\n파일 형식: {file_format}\n\n"
        prompt += "각 설정에 대한 주석을 추가하여 초보 개발자가 이해하기 쉽게 만들어주세요. 코드만 반환하고 설명은 주석으로 처리해주세요."
        
        return prompt

class AIService:
    """AI API 통신 서비스"""
    
    def generate_content(self, prompt):
        """
        AI API를 호출하여 설정 파일 생성
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.AI_API_KEY}"
        }
        
        payload = {
            "model": settings.AI_MODEL,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                        "type": "input_text",
                        "text": prompt
                        }
                    ]
                },
            ],
            "text": {
                "format": {
                    "type": "text"
                }
            },
            "reasoning": {
                "effort": "medium"
            },
            "tools": [],
            "store": True,
        }
        
        response = requests.post(settings.AI_API_URL, headers=headers, json=payload)

        print(response.json())  # 디버깅을 위한 응답 출력
        
        if response.status_code != 200:
            raise Exception(f"API 호출 실패: {response.text}")
        
        response_data = response.json()
        return response_data
        # return response_data['output'][0]['content'][0]['text']