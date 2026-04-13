from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .tests.xss import scan_xss
from .tests.sql_injection import scan_sql_injection
import re

@api_view(['POST'])
def scan_url(request):
    """
    Endpoint to receive and process URL scans
    """
    try:
        # Get URL from request
        url = request.data.get('url', '')
        
        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate URL format (basic validation)
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return Response(
                {'error': 'Invalid URL format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        print("Running XSS Scan")
        xss_results = scan_xss(url)
        print("XSS Scan Complete")

        
        print("Running SQL Injection Scan")
        sql_results = scan_sql_injection(url)
        print("SQL Injection Scan Complete")             
        
        threats_found = 0
        threat_categories = []
        
        if xss_results.get('vulnerable'):
            threats_found += 1
            threat_categories.append('XSS')
        
        if sql_results.get('vulnerable'):
            threats_found += 1
            threat_categories.append('SQL Injection')
        
        is_safe = threats_found == 0
        
        print("SCAN COMPLETE")
        print(f"Overall Status: {'SAFE' if is_safe else 'VULNERABLE'}")
        print(f"Threats Found: {threats_found}")
        
        # Build comprehensive response for frontend
        result = {
            'status': 'success',
            'message': 'Scan completed successfully',
            'url': url,
            'scan_summary': {
                'safe': is_safe,
                'threats_found': threats_found,
                'threat_categories': threat_categories if threat_categories else ['None'],
                'scan_date': None  # You can add timestamp if needed
            },
            'vulnerabilities': {
                'xss': xss_results,
                'sql_injection': sql_results
            }
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    