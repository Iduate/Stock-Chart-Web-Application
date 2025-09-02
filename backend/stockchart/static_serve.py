"""
Custom static file serving for Railway deployment
Handles MIME types correctly for CSS and JS files
"""

import os
import mimetypes
import logging
from django.http import HttpResponse, Http404
from django.conf import settings

# 로깅 설정
logger = logging.getLogger(__name__)

def serve_static_with_mime(request, path):
    """
    Custom static file serving with correct MIME types
    """
    # 디버깅용 로깅
    logger.info(f"Serving static file: {path}")
    print(f"DEBUG: Serving static file: {path}")
    
    # 정적 파일 경로 구성
    static_file_path = os.path.join(settings.STATIC_ROOT, path)
    
    # 디버깅: 파일 경로 확인
    print(f"DEBUG: Static file path: {static_file_path}")
    print(f"DEBUG: File exists: {os.path.exists(static_file_path)}")
    
    # 파일이 존재하지 않으면 404
    if not os.path.exists(static_file_path):
        print(f"DEBUG: File not found: {static_file_path}")
        raise Http404("Static file not found")
    
    # MIME 타입 결정
    content_type = 'text/plain'  # 기본값
    
    # 파일 확장자에 따른 MIME 타입 설정
    if path.endswith('.css'):
        content_type = 'text/css; charset=utf-8'
        print(f"DEBUG: Setting CSS MIME type for {path}")
    elif path.endswith('.js'):
        content_type = 'application/javascript; charset=utf-8'
        print(f"DEBUG: Setting JS MIME type for {path}")
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
    
    print(f"DEBUG: Final content type: {content_type}")
    
    try:
        # 바이너리 모드로 파일 읽기
        with open(static_file_path, 'rb') as f:
            file_content = f.read()
        
        print(f"DEBUG: File size: {len(file_content)} bytes")
        
        # HTTP 응답 생성
        response = HttpResponse(file_content, content_type=content_type)
        
        # 캐시 헤더 설정
        response['Cache-Control'] = 'public, max-age=86400'  # 1일 캐시
        response['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'
        
        # CORS 헤더 추가 (필요시)
        response['Access-Control-Allow-Origin'] = '*'
        
        # 디버깅 헤더 추가
        response['X-Served-By'] = 'Custom-Static-Server'
        response['X-Debug-Path'] = path
        response['X-Debug-Content-Type'] = content_type
        
        print(f"DEBUG: Response created successfully with content-type: {content_type}")
        
        return response
        
    except Exception as e:
        print(f"DEBUG: Error serving file: {str(e)}")
        logger.error(f"Error serving static file {path}: {str(e)}")
        raise Http404(f"Error serving static file: {str(e)}")
