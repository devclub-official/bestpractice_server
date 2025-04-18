from django.urls import path
from .views import (
    ConfigGeneratorView, ConfigHistoryListView, 
    BookmarkedConfigListView, PopularConfigListView,
    toggle_bookmark, update_config_title
)

urlpatterns = [
    path('generate-config/', ConfigGeneratorView.as_view(), name='generate-config'),
    path('config-history/', ConfigHistoryListView.as_view(), name='config-history'),
    path('bookmarked-configs/', BookmarkedConfigListView.as_view(), name='bookmarked-configs'),
    path('popular-configs/', PopularConfigListView.as_view(), name='popular-configs'),
    path('toggle-bookmark/<int:config_id>/', toggle_bookmark, name='toggle-bookmark'),
    path('update-config-title/<int:config_id>/', update_config_title, name='update-config-title'),
]#     """설정 파일 제목 업데이트"""