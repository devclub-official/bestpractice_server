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
        - JSON: JSON 객체로 파싱
        - YAML: Python 객체로 파싱
        - 기타: 원본 문자열 그대로 반환
        """
        if not obj.content:
            return {}
        
        # 파일 형식 확인
        file_format = obj.file_format if obj.file_format else 'json'
        print(f"File format: {file_format}")
        
        try:
            # YAML 파일 형식인 경우
            if file_format in ['yaml', 'yml']:
                try:
                    # YAML 파싱 시도
                    return yaml.safe_load(obj.content)
                except Exception as e:
                    return {"error": f"YAML 파싱 오류: {str(e)}", "raw": obj.content}
            
            # JSON 파일 형식인 경우
            elif file_format == 'json':
                try:
                    # 직접 JSON 파싱 시도
                    return json.loads(obj.content)
                except json.JSONDecodeError:
                    # 작은따옴표를 큰따옴표로 변환하여 다시 시도
                    try:
                        content_str = obj.content.replace("'", "\"")
                        return json.loads(content_str)
                    except json.JSONDecodeError:
                        # ast.literal_eval 시도
                        try:
                            return ast.literal_eval(obj.content)
                        except (ValueError, SyntaxError):
                            return {"error": "JSON 파싱 실패", "raw": obj.content}
            
            # JavaScript 설정 파일인 경우 (module.exports = {...})
            elif file_format in ['js', 'javascript']:
                # module.exports = {...} 형식에서 {...} 부분만 추출 시도
                if 'module.exports' in obj.content:
                    try:
                        json_part = obj.content.split('module.exports =')[1].split(';')[0].strip()
                        # 추출된 JSON 파트 파싱 시도
                        try:
                            return json.loads(json_part)
                        except json.JSONDecodeError:
                            # 작은따옴표를 큰따옴표로 변환
                            json_part = json_part.replace("'", "\"")
                            return json.loads(json_part)
                    except (IndexError, json.JSONDecodeError):
                        pass
                
                # 추출 실패시 원본 반환
                return {"content": obj.content, "format": "javascript"}
            
            # Python 설정 파일인 경우
            elif file_format in ['py', 'python']:
                # CONFIG = {...} 형식에서 {...} 부분만 추출 시도
                if 'CONFIG =' in obj.content:
                    try:
                        # Python 딕셔너리 파트 추출
                        py_dict_part = obj.content.split('CONFIG =')[1].strip()
                        # ast를 사용하여 안전하게 평가
                        return ast.literal_eval(py_dict_part)
                    except (IndexError, ValueError, SyntaxError):
                        pass
                
                # 추출 실패시 원본 반환
                return {"content": obj.content, "format": "python"}
            
            # 기타 텍스트 기반 형식 (properties, env 등)
            else:
                # 원본 텍스트 그대로 반환
                return {"content": obj.content, "format": file_format}
                
        except Exception as e:
            # 모든 파싱 실패시 에러 정보와 원본 반환
            return {"error": str(e), "raw": obj.content}
    
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