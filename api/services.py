import requests
import json
import re
import yaml  # pip install pyyaml
from django.conf import settings

class PromptGeneratorService:
    """프롬프트 생성 서비스"""
    
    def generate_prompt(self, data):
        """
        사용자 입력에 기반한 프롬프트 생성
        """
        language = data['language']
        framework = data['framework']
        file_format = data['file_format']
        selected_options = data['selected_options']
        
        prompt = f"""당신은 초보 개발자를 돕는 도우미입니다. 
            다음 조건에 맞는 설정 파일 전체를 생성해주세요:

            프로그래밍 언어: {language}
            프레임워크: {framework}
            필요한 기능 및 옵션:
        """
        
        # 수정된 부분: .items() 메서드 사용
        for option, value in selected_options.items():
            prompt += f"- {option}: {value}\n"
            
        prompt += f"\n파일 형식: {file_format}\n\n"
        # prompt += "각 설정에 대한 주석을 추가하여 초보 개발자가 이해하기 쉽게 만들어주세요. 코드만 반환하고 설명은 주석으로 처리해주세요."

        return prompt

class AIService:
    """AI API 통신 서비스"""
    
    def generate_content(self, prompt, file_format='json'):
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
            "temperature": 1,
            "max_output_tokens": 1000,
            "tools": [],
            "top_p": 1,
            "store": False,
        }
        
        response = requests.post(settings.AI_API_URL, headers=headers, json=payload)

        
        if response.status_code != 200:
            raise Exception(f"API 호출 실패: {response.text}")

        # 응답 데이터 파싱
        response_data = response.json()
        
        # content -> output -> content -> text 경로로 접근
        output_text = response_data['output'][0]['content'][0]['text']
        print(f"AI 응답: {output_text}")  # 디버깅용 
        
        # print(f"AI 응답 JSON: {json.loads(output_text)}")

        # JSON 파싱 (주석 제거)
        parsed_data = self.parse_json_with_comments(output_text)
        
        # 요청된 형식에 따라 처리
        if file_format in ['yaml', 'yml']:
            # YAML 형식으로 변환
            return self.convert_to_yaml(parsed_data)
        else:
            # 기본은 파싱된 데이터 그대로 반환
            return parsed_data
        
    def parse_json_with_comments(self, json_string):
        """
        주석이 포함된 JSON 문자열을 파싱하여 Python 객체로 변환합니다.
        
        Args:
            json_string: 주석이 포함된 JSON 문자열
            
        Returns:
            dict: 파싱된 JSON 객체
        """
        # 입력이 없거나 빈 문자열인 경우 처리
        if not json_string or json_string.strip() == '':
            print("입력된 JSON 문자열이 비어 있습니다.")
            return {}
        
        # 코드 블록 마커(```json, ```) 제거
        if '```json' in json_string and '```' in json_string:
            # JSON 코드 블록 내용만 추출
            json_start = json_string.find('```json') + 7
            json_end = json_string.rfind('```')
            json_string = json_string[json_start:json_end].strip()
        elif '```' in json_string:  # 언어 지정 없는 코드 블록
            json_start = json_string.find('```') + 3
            json_end = json_string.rfind('```')
            json_string = json_string[json_start:json_end].strip()
        
        # 처리 후 문자열이 비어있는지 확인
        if not json_string or json_string.strip() == '':
            print("코드 블록 제거 후 JSON 문자열이 비어 있습니다.")
            return {}
        
        # 한 줄 주석 제거 (// 이후의 내용)
        lines = json_string.split('\n')
        clean_lines = []
        
        for line in lines:
            # 따옴표 안에 있지 않은 // 찾기
            new_line = ""
            in_string = False
            escape_next = False
            i = 0
            
            while i < len(line):
                char = line[i]
                
                # 문자열 내부/외부 상태 추적
                if char == '"' and not escape_next:
                    in_string = not in_string
                
                # 이스케이프 문자 확인
                if char == '\\' and not escape_next:
                    escape_next = True
                else:
                    escape_next = False
                
                # 문자열 외부에서 주석 시작을 발견하면 중단
                if char == '/' and i + 1 < len(line) and line[i+1] == '/' and not in_string:
                    break
                
                new_line += char
                i += 1
            
            # 정리된 줄 추가 (공백 제거)
            clean_line = new_line.strip()
            if clean_line:  # 빈 줄이 아닌 경우만 추가
                clean_lines.append(clean_line)
        
        # 정리된 JSON 문자열 생성
        clean_json_string = '\n'.join(clean_lines)
        
        # 처리 후 문자열이 비어있는지 확인
        if not clean_json_string or clean_json_string.strip() == '':
            print("주석 제거 후 JSON 문자열이 비어 있습니다.")
            return {}
        
        # 마지막 요소 뒤의 쉼표 제거 (JSON 문법 오류 방지)
        clean_json_string = re.sub(r',(\s*[\]}])', r'\1', clean_json_string)
        
        # JSON 파싱
        try:
            return json.loads(clean_json_string)
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            print(f"정리된 JSON 문자열: {clean_json_string}")
            
            # JSON 형식이 아닌 경우에 대한 대체 처리
            try:
                # 1. 작은따옴표를 큰따옴표로 바꿔서 시도
                replaced_quotes = clean_json_string.replace("'", "\"")
                return json.loads(replaced_quotes)
            except json.JSONDecodeError:
                try:
                    # 2. ast.literal_eval 시도 (Python 표현식으로 해석)
                    import ast
                    return ast.literal_eval(clean_json_string)
                except (ValueError, SyntaxError):
                    # 3. AI 응답이 일반 텍스트인 경우 처리
                    if '{' not in clean_json_string and '}' not in clean_json_string:
                        return {"text_content": clean_json_string}
                    else:
                        # 4. 최후의 수단으로 원본 문자열을 반환
                        return {"error": str(e), "raw_content": json_string}

    def convert_to_yaml(self, data):
        """
        Python 객체를 YAML 형식 문자열로 변환
        
        Args:
            data: 변환할 Python 객체 (주로 dict)
            
        Returns:
            str: YAML 형식 문자열
        """
        try:
            # PyYAML 라이브러리를 사용하여 변환
            # default_flow_style=False: 블록 스타일로 출력 (가독성 향상)
            # sort_keys=False: 키 순서 유지
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"YAML 변환 오류: {e}")
            # 변환 실패 시 원본 데이터 JSON 문자열로 반환
            return json.dumps(data, indent=2)