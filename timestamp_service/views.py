from django.http import JsonResponse

from timestamp_service.client import get_timestamp


def test_timestamp(request):
    """Simple view to test if the timestamp service is working"""
    timestamp = get_timestamp()

    if timestamp:
        return JsonResponse({
            'status': 'success',
            'timestamp': timestamp
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Could not connect to timestamp service'
        }, status=500)
