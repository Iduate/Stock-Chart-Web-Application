"""
Custom static file serving for Railway deployment
Handles MIME types correctly for CSS and JS files
"""

import os
import mimetypes
from django.http import HttpResponse, Http404
from django.conf import settings

def serve_static_with_mime(request, path):
    """
    Custom static file serving with correct MIME types
    """
    # 정적 파일 경로 구성
    static_file_path = os.path.join(settings.STATIC_ROOT, path)
    
    # 파일이 존재하지 않으면 404
    if not os.path.exists(static_file_path):
        raise Http404("Static file not found")
    
    # MIME 타입 결정
    content_type = 'text/plain'  # 기본값
    
    # 파일 확장자에 따른 MIME 타입 설정
    if path.endswith('.css'):
        content_type = 'text/css; charset=utf-8'
    elif path.endswith('.js'):
        content_type = 'application/javascript; charset=utf-8'
    elif path.endswith('.map'):
        content_type = 'application/json'
    elif path.endswith('.ico'):
        content_type = 'image/x-icon'
    elif path.endswith('.png'):
        content_type = 'image/png'
    elif path.endswith('.jpg') or path.endswith('.jpeg'):
        content_type = 'image/jpeg'
    elif path.endswith('.gif'):
        content_type = 'image/gif'
    elif path.endswith('.svg'):
        content_type = 'image/svg+xml'
    elif path.endswith('.woff'):
        content_type = 'font/woff'
    elif path.endswith('.woff2'):
        content_type = 'font/woff2'
    elif path.endswith('.ttf'):
        content_type = 'font/ttf'
    elif path.endswith('.eot'):
        content_type = 'application/vnd.ms-fontobject'
    else:
        # 기타 파일은 mimetypes 모듈 사용
        content_type, _ = mimetypes.guess_type(static_file_path)
        if not content_type:
            content_type = 'application/octet-stream'
    
    try:
        # 바이너리 모드로 파일 읽기
        with open(static_file_path, 'rb') as f:
            file_content = f.read()
        
        # HTTP 응답 생성
        response = HttpResponse(file_content, content_type=content_type)
        
        # 캐시 헤더 설정
        response['Cache-Control'] = 'public, max-age=86400'  # 1일 캐시
        response['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'
        
        # CORS 헤더 추가 (필요시)
        response['Access-Control-Allow-Origin'] = '*'
        
        return response
        
    except Exception as e:
        raise Http404(f"Error serving static file: {str(e)}")
