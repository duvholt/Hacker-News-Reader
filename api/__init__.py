from django.conf import settings
from api.backends import algolia, builtin


API_BACKEND = hasattr(settings, 'API_BACKEND')
if API_BACKEND:
    API_BACKEND = settings.API_BACKEND.lower()

if API_BACKEND == 'algolia':
    API = algolia.AlgoliaAPI()
elif API_BACKEND == 'builtin':
    API = builtin.BuiltinAPI()
else:
    API = builtin.BuiltinAPI()
