from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ConfigRequestSerializer, GeneratedConfigSerializer
from .services import PromptGeneratorService, AIService
from generator.models import GeneratedConfig
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes

class ConfigGeneratorView(APIView):
    """설정 파일 생성 API 뷰"""
    
    def post(self, request):
        serializer = ConfigRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 유효한 데이터로 설정 파일 생성
        prompt_service = PromptGeneratorService()
        ai_service = AIService()
        
        # try:
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
            content=generated_content,
            title=serializer.validated_data.get('title', '')
        )
        
        # 파일명 및 MIME 타입 생성
        filename = self._generate_filename(serializer.validated_data)
        mime_type = self._generate_mime_type(serializer.validated_data['file_format'])
        
        return Response({
            'id': config.id,
            'content': generated_content,
            'filename': filename,
            'mime_type': mime_type,
            'title': config.title if config.title else None,
            'created_at': config.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }, status=status.HTTP_200_OK)
            
        # except Exception as e:
        #     return Response(
        #         {'error': f'설정 파일 생성 중 오류가 발생했습니다: {str(e)}'},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
    
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


class ConfigHistoryListView(generics.ListAPIView):
    """설정 파일 생성 히스토리 목록 조회"""
    serializer_class = GeneratedConfigSerializer
    
    def get_queryset(self):
        """최근에 생성된 순서로 히스토리 조회"""
        return GeneratedConfig.objects.all().order_by('-created_at')
    
    def get_serializer_context(self):
        return {'request': self.request}

class BookmarkedConfigListView(generics.ListAPIView):
    """북마크된 설정 파일 목록 조회"""
    serializer_class = GeneratedConfigSerializer
    
    def get_queryset(self):
        """현재 사용자가 북마크한 설정 파일 조회"""
        return GeneratedConfig.objects.filter(
            user_bookmarks__user=self.request.user
        ).order_by('-user_bookmarks__created_at')
    
    def get_serializer_context(self):
        return {'request': self.request}

class PopularConfigListView(generics.ListAPIView):
    """인기 있는 설정 파일 목록 조회 (북마크 수 기준)"""
    serializer_class = GeneratedConfigSerializer
    
    def get_queryset(self):
        """북마크 수가 많은 순서로 인기 설정 파일 조회"""
        return GeneratedConfig.objects.filter(
            bookmark_count__gt=0
        ).order_by('-bookmark_count', '-created_at')
    
    def get_serializer_context(self):
        return {'request': self.request}

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_bookmark(request, config_id):
    """설정 파일 북마크 토글"""
    try:
        config = GeneratedConfig.objects.get(id=config_id)
        
        # 현재 사용자의 북마크 확인
        bookmark, created = UserBookmark.objects.get_or_create(
            user=request.user, 
            config=config
        )
        
        if not created:  # 이미 북마크가 있으면 삭제
            bookmark.delete()
            config.bookmark_count = max(0, config.bookmark_count - 1)  # 북마크 카운트 감소
            config.save()
            return Response({'status': 'unbookmarked'}, status=status.HTTP_200_OK)
        
        # 북마크가 생성됨
        config.bookmark_count += 1  # 북마크 카운트 증가
        config.save()
        return Response({'status': 'bookmarked'}, status=status.HTTP_201_CREATED)
        
    except GeneratedConfig.DoesNotExist:
        return Response(
            {'error': '설정 파일을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_config_title(request, config_id):
    """설정 파일 제목 업데이트"""
    try:
        config = GeneratedConfig.objects.get(id=config_id)
        
        title = request.data.get('title', '')
        config.title = title
        config.save()
        
        return Response({'status': 'updated', 'title': title}, status=status.HTTP_200_OK)
        
    except GeneratedConfig.DoesNotExist:
        return Response(
            {'error': '설정 파일을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )