from rest_framework import serializers
from generator.models import GeneratedConfig

class ConfigRequestSerializer(serializers.Serializer):
    """설정 파일 생성 요청을 위한 시리얼라이저"""
    language = serializers.CharField(required=True)
    framework = serializers.CharField(required=True)
    features = serializers.ListField(child=serializers.CharField(), required=True)
    file_format = serializers.CharField(required=True)
    
class GeneratedConfigSerializer(serializers.ModelSerializer):
    """생성된 설정 파일을 위한 시리얼라이저"""
    class Meta:
        model = GeneratedConfig
        fields = '__all__'