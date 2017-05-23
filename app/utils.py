from django.conf import settings


def get_absolute_uri(url, request=None):
    if request:
        url = request.build_absolute_uri(url)
    else:
        url = '%s%s%s' % (
            settings.PROTOCOL,
            settings.DOMAIN,
            '/%s/' % url.strip('/')
        )

    return url
