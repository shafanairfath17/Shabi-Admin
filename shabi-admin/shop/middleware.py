from django.conf import settings
CSP = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https://res.cloudinary.com; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
def csp(get_response):
    def mw(request):
        r = get_response(request)
        if not request.path.startswith("/" + settings.ADMIN_URL):  # admin uses inline assets
            r.headers.setdefault("Content-Security-Policy", CSP)
        r.headers.setdefault("X-Content-Type-Options", "nosniff")
        r.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return r
    return mw
