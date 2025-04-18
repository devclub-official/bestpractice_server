from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ConfigRequestSerializer, GeneratedConfigSerializer
from .services import PromptGeneratorService, AIService
from generator.models import GeneratedConfig

class ConfigGeneratorView(APIView):
    """설정 파일 생성 API 뷰"""
    
    def post(self, request):
        serializer = ConfigRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 유효한 데이터로 설정 파일 생성
        prompt_service = PromptGeneratorService()
        ai_service = AIService()
        
        try:
            # 프롬프트 생성
            prompt = prompt_service.generate_prompt(serializer.validated_data)
            
            # AI API 호출
            generated_content = ai_service.generate_content(prompt)
            
            # 생성된 설정 파일 저장
            config = GeneratedConfig.objects.create(
                language=serializer.validated_data['language'],
                framework=serializer.validated_data['framework'],
                features=serializer.validated_data['features'],
                file_format=serializer.validated_data['file_format'],
                content=generated_content
            )
            
            # 파일명 및 MIME 타입 생성
            filename = self._generate_filename(serializer.validated_data)
            mime_type = self._generate_mime_type(serializer.validated_data['file_format'])
            
            return Response({
                'content': generated_content,
                'filename': filename,
                'mime_type': mime_type
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'설정 파일 생성 중 오류가 발생했습니다: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_filename(self, data):
        """요청 데이터에 따른 파일명 생성"""
        framework = data['framework']
        file_format = data['file_format']
        
        if framework == 'django':
            return 'settings.py'
        elif framework in ['spring', 'springboot']:
            return f'application.{file_format}'
        elif framework in ['react', 'vue', 'angular']:
            return 'package.json'
        
        return f'config.{file_format}'
    
    def _generate_mime_type(self, file_format):
        """파일 형식에 따른 MIME 타입 생성"""
        mime_types = {
            'py': 'text/x-python',
            'properties': 'text/plain',
            'yaml': 'text/yaml',
            'yml': 'text/yaml',
            'json': 'application/json',
            'js': 'application/javascript'
        }
        
        return mime_types.get(file_format, 'text/plain')