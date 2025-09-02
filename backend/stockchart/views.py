from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
import mimetypes
from django.conf import settings

def serve_static_file(request, path):
    """정적 파일을 올바른 MIME 타입으로 서빙"""
    static_file_path = os.path.join(settings.STATIC_ROOT, path)
    
    if not os.path.exists(static_file_path):
        raise Http404("Static file not found")
    
    # MIME 타입 결정
    content_type, _ = mimetypes.guess_type(static_file_path)
    
    # CSS와 JS 파일의 MIME 타입을 명시적으로 설정
    if path.endswith('.css'):
        content_type = 'text/css'
    elif path.endswith('.js'):
        content_type = 'application/javascript'
    elif path.endswith('.map'):
        content_type = 'application/json'
    
    try:
        with open(static_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Cache-Control'] = 'max-age=86400'  # 1일 캐시
            return response
    except Exception:
        raise Http404("Static file not found")

def home(request):
    """홈페이지 뷰 - frontend/index.html 서빙"""
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
