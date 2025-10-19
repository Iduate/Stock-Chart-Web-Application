from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import os
import datetime
from django.conf import settings


@csrf_exempt
def health_check(request):
    """
    Health check endpoint for deployment monitoring
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JsonResponse({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'database': db_status,
        'version': '1.0.0'
    })

def serve_html_page(request, page_name=None):
    """다중 페이지 HTML 파일들을 서빙하는 뷰"""
    # 기본 페이지는 home.html
    if not page_name:
        page_name = 'home.html'
    elif not page_name.endswith('.html'):
        page_name += '.html'
    
    # 허용된 페이지 목록 (보안을 위해)
    allowed_pages = [
        'home.html', 'charts.html', 'prediction.html',
        'my-predictions.html', 'ranking.html', 'events.html',
        'subscription.html', 'payment.html', 'partners.html',
        'index.html',
        # Payments/crypto pages
        'buy-crypto.html', 'payment-success.html', 'payment-cancel.html'
    ]
    
    if page_name not in allowed_pages:
        raise Http404(f"Page '{page_name}' not found")
    
    # frontend 디렉토리의 HTML 파일 경로
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', page_name)
    
    try:
        with open(frontend_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Ensure UTF-8 charset for proper Korean text rendering
        return HttpResponse(content, content_type='text/html; charset=utf-8')

    except FileNotFoundError:
        raise Http404(f"Page '{page_name}' not found")
    except Exception as e:
        return HttpResponse(
            f'<h1>Error loading page</h1><p>{str(e)}</p>',
            content_type='text/html; charset=utf-8',
            status=500,
        )

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
        
        # Load mobile fixes CSS
        mobile_fixes_css = ""
        mobile_fixes_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'css', 'mobile-fixes.css')
        if os.path.exists(mobile_fixes_path):
            with open(mobile_fixes_path, 'r', encoding='utf-8') as f:
                mobile_fixes_css = f.read()
                
        # CSS 링크들을 인라인 스타일로 교체
        content = content.replace('<link rel="stylesheet" href="css/style.css">', f'<style>{inline_css}</style>')
        content = content.replace('<link rel="stylesheet" href="css/mobile-fixes.css">', f'<style>{mobile_fixes_css}</style>')
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

        # Ensure UTF-8 charset for proper Korean text rendering
        return HttpResponse(content, content_type='text/html; charset=utf-8')

    except FileNotFoundError as e:
        # 만약 frontend 파일이 없으면 기존 템플릿 사용
        return render(request, 'home.html')
    except Exception as e:
        # 에러 발생시 디버깅 정보와 함께 표시
        return HttpResponse(
            f'<h1>Error loading page</h1><p>{str(e)}</p>',
            content_type='text/html; charset=utf-8',
            status=500,
        )

@api_view(['GET'])
def api_status(request):
    """API 상태 확인"""
    # 직접 환경변수 체크
    env_check = {
        'ALPHA_VANTAGE_API_KEY': os.environ.get('ALPHA_VANTAGE_API_KEY', 'NOT_SET'),
        'TWELVE_DATA_API_KEY': os.environ.get('TWELVE_DATA_API_KEY', 'NOT_SET'),
        'FINNHUB_API_KEY': os.environ.get('FINNHUB_API_KEY', 'NOT_SET'),
        'POLYGON_API_KEY': os.environ.get('POLYGON_API_KEY', 'NOT_SET'),
        'TIINGO_API_KEY': os.environ.get('TIINGO_API_KEY', 'NOT_SET'),
        'MARKETSTACK_API_KEY': os.environ.get('MARKETSTACK_API_KEY', 'NOT_SET'),
    }
    
    # 설정에서 확인
    settings_check = {
        'alpha_vantage': getattr(settings, 'ALPHA_VANTAGE_API_KEY', 'NOT_IN_SETTINGS'),
        'twelve_data': getattr(settings, 'TWELVE_DATA_API_KEY', 'NOT_IN_SETTINGS'),
        'finnhub': getattr(settings, 'FINNHUB_API_KEY', 'NOT_IN_SETTINGS'),
        'polygon': getattr(settings, 'POLYGON_API_KEY', 'NOT_IN_SETTINGS'),
        'tiingo': getattr(settings, 'TIINGO_API_KEY', 'NOT_IN_SETTINGS'),
        'marketstack': getattr(settings, 'MARKETSTACK_API_KEY', 'NOT_IN_SETTINGS'),
    }
    
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
        },
        'direct_env_check': {k: 'SET' if v != 'NOT_SET' else 'NOT_SET' for k, v in env_check.items()},
        'settings_values': {k: 'SET' if v != 'NOT_IN_SETTINGS' else 'NOT_IN_SETTINGS' for k, v in settings_check.items()},
        'raw_env_sample': os.environ.get('ALPHA_VANTAGE_API_KEY', 'NONE')[:10] + '...' if os.environ.get('ALPHA_VANTAGE_API_KEY') else 'NONE'
    })

@api_view(['GET'])
def market_stocks_redirect(request):
    """Redirect /api/market/stocks/ to market_data view"""
    from market_data.views import get_popular_stocks
    return get_popular_stocks(request)
