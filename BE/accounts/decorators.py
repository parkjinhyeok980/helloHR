from functools import wraps
from django.http import JsonResponse
from django.views.decorators.cache import never_cache


def account_required(view):
    @wraps(view)
    @never_cache
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'detail': '로그인이 필요합니다.',
                                 'code': getattr(request, 'jwt_error', None) or 'authentication_required'}, status=401)
        return view(request, *args, **kwargs)
    return wrapped
