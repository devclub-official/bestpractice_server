import json
import ast
import re
import yaml
from rest_framework import serializers
from generator.models import GeneratedConfig

class ConfigRequestSerializer(serializers.Serializer):
    """설정 파일 생성 요청을 위한 시리얼라이저"""
    language = serializers.CharField(required=True)
    framework = serializers.CharField(required=True)
    selected_options = serializers.JSONField(
        help_text="키는 옵션 키(auth, network 등), 값은 해당 옵션의 설정값"
    )
    file_format = serializers.CharField(required=True)

    # def validate_selected_options(self, value):
    #     """옵션 키가 유효한지 검증"""
    #     valid_keys = [key for key, _ in ConfigOptionChoices.CHOICES]
        
    #     for key in value.keys():
    #         if key not in valid_keys:
    #             raise serializers.ValidationError(f"'{key}'는 유효하지 않은 옵션 키입니다.")
        
    #     return value
    
class GeneratedConfigSerializer(serializers.ModelSerializer):
    """생성된 설정 파일을 위한 시리얼라이저"""
    content = serializers.SerializerMethodField()
    # selected_options = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedConfig
        fields = '__all__'
    
    def get_content(self, obj):
        """
        content 필드를 파일 형식에 맞게 파싱
        """
        if not obj.content:
            return {}
        
        # 파일 형식 확인
        file_format = obj.file_format if obj.file_format else 'json'
        print(f"File format: {file_format}")
        
        try:
            # 먼저 content가 JSON 문자열인지 확인 (text_content 필드를 포함하는 경우)
            content_to_parse = obj.content
            try:
                # content가 JSON 문자열인 경우 파싱
                content_json = json.loads(obj.content)
                if isinstance(content_json, dict) and 'text_content' in content_json:
                    # 실제 콘텐츠는 text_content 필드에 있음
                    content_to_parse = content_json['text_content']
            except (json.JSONDecodeError, TypeError):
                # JSON이 아니면 원본 그대로 사용
                pass
                
            # YAML 파일 형식인 경우
            if file_format in ['yaml', 'yml']:
                try:
                    # 접두어 'yaml' 제거
                    if content_to_parse.startswith("yaml\n"):
                        content_to_parse = content_to_parse[5:]
                    
                    # YAML 직접 수정하는 대신 안전한 접근법: 수동으로 구성된 YAML 문자열 생성
                    formatted_yaml = self.manually_format_yaml(content_to_parse)
                    
                    # 디버깅 출력
                    print("원본 YAML 내용:")
                    print(content_to_parse[:200] + "..." if len(content_to_parse) > 200 else content_to_parse)
                    print("\n수정된 YAML 내용:")
                    print(formatted_yaml[:200] + "..." if len(formatted_yaml) > 200 else formatted_yaml)
                    
                    # YAML에서는 파싱이 항상 어려우므로 직접 문자열 형태로 반환
                    return {"text_content": formatted_yaml}
                    
                except Exception as e:
                    print(f"YAML 처리 오류: {str(e)}")
                    # 오류 발생 시 원본 텍스트 반환
                    return {"text_content": content_to_parse, "error": str(e)}
            
            # JSON 파일 형식인 경우
            elif file_format == 'json':
                try:
                    return json.loads(content_to_parse)
                except json.JSONDecodeError:
                    try:
                        content_str = content_to_parse.replace("'", "\"")
                        return json.loads(content_str)
                    except json.JSONDecodeError:
                        try:
                            return ast.literal_eval(content_to_parse)
                        except (ValueError, SyntaxError):
                            return {"text_content": content_to_parse, "error": "JSON 파싱 실패"}
            
            # 기타 형식
            else:
                return {"text_content": content_to_parse, "format": file_format}
                
        except Exception as e:
            return {"error": str(e), "text_content": obj.content}
    
    def manually_format_yaml(self, yaml_text):
        """
        YAML 파싱 대신 텍스트 처리로 들여쓰기와 콜론 처리
        """
        lines = yaml_text.split('\n')
        result = []
        structure = {}  # 키: 깊이
        current_path = []
        
        # 라인별 처리
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 빈 줄이나 주석은 그대로 유지
            if not stripped or stripped.startswith('#'):
                result.append(stripped)
                continue
            
            # 키:값 패턴 처리
            if ':' in stripped:
                # 키와 값 분리
                key_parts = stripped.split(':', 1)
                key = key_parts[0].strip()
                value = key_parts[1].strip() if len(key_parts) > 1 else ""
                
                # 이전 라인 확인하여 계층 구조 파악
                if i > 0 and not lines[i-1].strip().startswith('#') and ':' in lines[i-1].strip():
                    prev_key_parts = lines[i-1].strip().split(':', 1)
                    prev_key = prev_key_parts[0].strip()
                    prev_value = prev_key_parts[1].strip() if len(prev_key_parts) > 1 else ""
                    
                    # 이전 키가 값이 없으면 새 섹션 시작
                    if not prev_value and prev_key not in structure:
                        current_path.append(prev_key)
                        structure[prev_key] = len(current_path) - 1
                
                # 현재 키의 깊이 결정
                if not current_path:
                    depth = 0
                else:
                    # 현재 키가 이미 구조에 있으면 해당 깊이 사용
                    if key in structure:
                        depth = structure[key]
                    else:
                        # 아니면 현재 경로 길이 기반 깊이 설정
                        depth = len(current_path)
                        structure[key] = depth
                
                # 값에 콜론이 있으면 따옴표로 감싸기
                if value and ':' in value and not (value.startswith('"') and value.endswith('"')):
                    value = f'"{value}"'
                
                # 들여쓰기 적용
                indent = '  ' * depth
                if value:
                    result.append(f"{indent}{key}: {value}")
                else:
                    result.append(f"{indent}{key}:")
            else:
                # 콜론이 없는 라인 (거의 없음)
                result.append(stripped)
        
        return '\n'.join(result)
    
    # def get_selected_options(self, obj):
    #     """features 필드를, 만약 문자열로 저장되어 있다면 리스트로 변환"""
    #     if not obj.selected_options:
    #         return []
            
    #     features = obj.selected_options
        
    #     # features가 이미 리스트인 경우
    #     if isinstance(features, list):
    #         result = []
    #         for feature in features:
    #             # 각 항목이 문자열로 저장된 리스트/딕셔너리인지 확인
    #             if isinstance(feature, str) and (feature.startswith('[') or feature.startswith('{')):
    #                 try:
    #                     # JSON 파싱 시도
    #                     parsed_feature = json.loads(feature)
    #                     result.append(parsed_feature)
    #                 except json.JSONDecodeError:
    #                     # ast.literal_eval 시도
    #                     try:
    #                         parsed_feature = ast.literal_eval(feature)
    #                         result.append(parsed_feature)
    #                     except (ValueError, SyntaxError):
    #                         result.append(feature)
    #             else:
    #                 result.append(feature)
    #         return result
        
    #     # features가 문자열인 경우 (직렬화된 JSON)
    #     if isinstance(features, str):
    #         try:
    #             return json.loads(features)
    #         except json.JSONDecodeError:
    #             try:
    #                 return ast.literal_eval(features)
    #             except (ValueError, SyntaxError):
    #                 return features
                    
    #     return features