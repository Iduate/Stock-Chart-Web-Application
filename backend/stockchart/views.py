from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
from django.conf import settings

def home(request):
    """홈페이지 뷰 - frontend/index.html 서빙 (CSS/JS 인라인 포함)"""
    # frontend 디렉토리의 index.html 파일 경로
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'index.html')
    
    try:
        with open(frontend_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # CSS 파일들을 인라인으로 포함
        css_files = ['style.css', 'market-data.css']
        inline_css = ""
        
        for css_file in css_files:
            css_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'css', css_file)
            if os.path.exists(css_path):
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                    inline_css += f"\n/* {css_file} */\n{css_content}\n"
        
        # JS 파일들을 인라인으로 포함
        js_files = ['app.js']
        inline_js = ""
        
        for js_file in js_files:
            js_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'js', js_file)
            if os.path.exists(js_path):
                with open(js_path, 'r', encoding='utf-8') as f:
                    js_content = f.read()
                    inline_js += f"\n/* {js_file} */\n{js_content}\n"
        
        # CSS 링크들을 인라인 스타일로 교체
        content = content.replace('<link rel="stylesheet" href="css/style.css">', f'<style>{inline_css}</style>')
        content = content.replace('<link rel="stylesheet" href="css/market-data.css">', '')
        
        # JS 스크립트들을 인라인으로 교체
        content = content.replace('<script src="js/app.js"></script>', f'<script>{inline_js}</script>')
        
        # 기타 정적 파일 경로는 그대로 유지 (이미지 등)
        static_url = settings.STATIC_URL
        if not static_url.endswith('/'):
            static_url += '/'
            
        content = content.replace('src="images/', f'src="{static_url}images/')
        content = content.replace('href="favicon.ico"', f'href="{static_url}favicon.ico"')
        
        # 디버깅 정보 추가
        content = content.replace('</head>', f'<!-- Inline CSS/JS embedded | API Keys Configured | DEBUG: {settings.DEBUG} -->\n</head>')
        
        return HttpResponse(content, content_type='text/html')
        
    except FileNotFoundError as e:
        # 만약 frontend 파일이 없으면 기존 템플릿 사용
        return render(request, 'home.html')
    except Exception as e:
        # 에러 발생시 디버깅 정보와 함께 표시
        return HttpResponse(f'<h1>Error loading page</h1><p>{str(e)}</p>', content_type='text/html')

@api_view(['GET'])
def api_status(request):
    """API 상태 확인"""
    # API 키 상태 확인 (보안을 위해 키 값은 노출하지 않음)
    api_keys_status = {
        'alpha_vantage': bool(getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)),
        'twelve_data': bool(getattr(settings, 'TWELVE_DATA_API_KEY', None)),
        'finnhub': bool(getattr(settings, 'FINNHUB_API_KEY', None)),
        'polygon': bool(getattr(settings, 'POLYGON_API_KEY', None)),
        'tiingo': bool(getattr(settings, 'TIINGO_API_KEY', None)),
        'marketstack': bool(getattr(settings, 'MARKETSTACK_API_KEY', None)),
    }
    
    return Response({
        'status': 'success',
        'message': '스톡차트 API가 정상 작동중입니다',
        'version': '1.0.0',
        'debug_mode': settings.DEBUG,
        'api_keys_configured': api_keys_status,
        'available_apis': sum(api_keys_status.values()),
        'environment_variables': {
            'DEBUG': os.environ.get('DEBUG', 'Not Set'),
            'RAILWAY_PROJECT_ID': bool(os.environ.get('RAILWAY_PROJECT_ID')),
            'ALPHA_VANTAGE_API_KEY': bool(os.environ.get('ALPHA_VANTAGE_API_KEY')),
        }
    })

@api_view(['GET'])
def market_stocks_redirect(request):
    """Redirect /api/market/stocks/ to market_data view"""
    from market_data.views import get_popular_stocks
    return get_popular_stocks(request)
