from django.utils import translation


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.headers.get("Accept-Language", "ru")[:2]
        if lang in ("ru", "uz", "en"):
            translation.activate(lang)
        response = self.get_response(request)
        return response
