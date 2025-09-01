from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

def home(request):
    """홈페이지 뷰"""
    return render(request, 'home.html')

@api_view(['GET'])
def api_status(request):
    """API 상태 확인"""
    return Response({
        'status': 'success',
        'message': '스톡차트 API가 정상 작동중입니다',
        'version': '1.0.0'
    })
