from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
from django.conf import settings

def home(request):
    """홈페이지 뷰 - frontend/index.html 서빙"""
    # frontend 디렉토리의 index.html 파일 경로
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'index.html')
    
    try:
        with open(frontend_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # CSS와 JS 파일 경로를 Django static URL로 변경
        content = content.replace('href="css/', f'href="{settings.STATIC_URL}css/')
        content = content.replace('src="js/', f'src="{settings.STATIC_URL}js/')
        content = content.replace('src="images/', f'src="{settings.STATIC_URL}images/')
        
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        # 만약 frontend 파일이 없으면 기존 템플릿 사용
        return render(request, 'home.html')

@api_view(['GET'])
def api_status(request):
    """API 상태 확인"""
    return Response({
        'status': 'success',
        'message': '스톡차트 API가 정상 작동중입니다',
        'version': '1.0.0'
    })

@api_view(['GET'])
def market_stocks_redirect(request):
    """Redirect /api/market/stocks/ to market_data view"""
    from market_data.views import get_popular_stocks
    return get_popular_stocks(request)
