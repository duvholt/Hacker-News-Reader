from django.conf import settings
from api.backends import algolia, builtin, firebase


API_BACKEND = hasattr(settings, 'API_BACKEND')
if API_BACKEND:
    API_BACKEND = settings.API_BACKEND.lower()

if API_BACKEND == 'algolia':
    API = algolia.AlgoliaAPI()
elif API_BACKEND == 'builtin':
    API = builtin.BuiltinAPI()
if API_BACKEND == 'firebase':
    API = firebase.FirebaseAPI()
else:
    API = builtin.BuiltinAPI()
