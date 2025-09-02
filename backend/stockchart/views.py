from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
from django.conf import settings

def home(request):
    """홈페이지 뷰 - frontend/index.html 서빙"""
    # static 파일 요청은 WhiteNoise가 처리하도록 함
    if request.path.startswith('/static/'):
        from django.http import Http404
        raise Http404("Static file not found")
    
    # frontend 디렉토리의 index.html 파일 경로
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'index.html')
    
    try:
        with open(frontend_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # CSS와 JS 파일 경로를 Django static URL로 변경
        # Railway에서도 작동하도록 절대 경로로 변경
        static_url = settings.STATIC_URL
        if not static_url.endswith('/'):
            static_url += '/'
            
        content = content.replace('href="css/', f'href="{static_url}css/')
        content = content.replace('src="js/', f'src="{static_url}js/')
        content = content.replace('src="images/', f'src="{static_url}images/')
        content = content.replace('href="favicon.ico"', f'href="{static_url}favicon.ico"')
        
        # 디버깅을 위해 실제 static URL을 HTML 주석으로 추가
        content = content.replace('</head>', f'<!-- Static URL: {static_url} -->\n</head>')
        
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
