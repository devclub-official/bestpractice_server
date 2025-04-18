from django.db import models

# Create your models here.

# 옵션 선택을 위한 상수 정의
class ConfigOptionChoices:
    """설정 옵션 선택지 정의"""
    AUTH = 'auth'
    NETWORK = 'network'
    EMAIL = 'email'
    ENV = 'env'
    LOGGING = 'logging'
    FILE = 'file'
    CACHE = 'cache'
    SCHEDULING = 'scheduling'
    TEST = 'test'
    API_DOC = 'api_doc'
    DATABASE = 'database'
    
    CHOICES = [
        (AUTH, '인증/보안'),
        (NETWORK, '네트워크'),
        (EMAIL, '이메일'),
        (ENV, '환경 변수'),
        (LOGGING, '로깅'),
        (FILE, '파일'),
        (CACHE, '캐시'),
        (SCHEDULING, '스케쥴링'),
        (TEST, '테스트'),
        (API_DOC, 'API 문서화'),
        (DATABASE, '데이터베이스'),
    ]
    
    @classmethod
    def get_display_name(cls, key):
        """키에 해당하는 표시 이름 반환"""
        for option_key, display_name in cls.CHOICES:
            if option_key == key:
                return display_name
        return key

class GeneratedConfig(models.Model):
    """생성된 설정 파일 기록"""
    # 기본 정보
    language = models.CharField(max_length=50, help_text="프로그래밍 언어 (예: javascript, python)")
    framework = models.CharField(max_length=50, help_text="프레임워크 (예: react, django)")
    
    # 선택된 옵션들 (JSONField로 저장)
    # 예: {"auth": {"type": "jwt"}, "database": {"engine": "mysql"}}
    selected_options = models.JSONField(default=dict, help_text="사용자가 선택한 옵션 및 설정값")
    
    # 파일 정보
    file_format = models.CharField(max_length=20, blank=True, null=True, help_text="파일 형식 (예: json, yaml)")
    filename = models.CharField(max_length=100, blank=True, null=True, help_text="파일명")
    mime_type = models.CharField(max_length=50, blank=True, null=True, help_text="MIME 타입")
    
    # 생성된 콘텐츠
    content = models.TextField(help_text="생성된 설정 파일 내용")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 북마크 관련
    is_bookmarked = models.BooleanField(default=False)
    # bookmark_count = models.IntegerField(default=0)
    
    # 제목
    title = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        title_display = self.title if self.title else f"{self.framework} config"
        return f"{title_display} ({self.file_format}) - {self.created_at}"