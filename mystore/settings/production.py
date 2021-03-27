import os
import random
import string

from .base import *  # noqa: F403

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
BASE_URL = 'http://localhost:8000'

if ELASTICSEARCH_ENDPOINT:
    from elasticsearch import RequestsHttpConnection
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND': 'wagtail.search.backends.elasticsearch2',
            'HOSTS': [{
                'host': ELASTICSEARCH_ENDPOINT,
                'port': int(os.getenv('ELASTICSEARCH_PORT', '9200')),
                'use_ssl': os.getenv('ELASTICSEARCH_USE_SSL', 'off') == 'on',
                'verify_certs': os.getenv('ELASTICSEARCH_VERIFY_CERTS', 'off') == 'on',
            }],
            'OPTIONS': {
                'connection_class': RequestsHttpConnection,
            },
        }
    }

    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        from aws_requests_auth.aws_auth import AWSRequestsAuth
        WAGTAILSEARCH_BACKENDS['default']['HOSTS'][0]['http_auth'] = AWSRequestsAuth(
            aws_access_key=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_token=os.getenv('AWS_SESSION_TOKEN', ''),
            aws_host=ELASTICSEARCH_ENDPOINT,
            aws_region=AWS_REGION,
            aws_service='es',
        )
    elif AWS_REGION:
        # No API keys in the environ, so attempt to discover them with Boto instead, per:
        # http://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials
        # This may be useful if your credentials are obtained via EC2 instance meta data.
        from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
        WAGTAILSEARCH_BACKENDS['default']['HOSTS'][0]['http_auth'] = BotoAWSRequestsAuth(
            aws_host=ELASTICSEARCH_ENDPOINT,
            aws_region=AWS_REGION,
            aws_service='es',
        )

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

if 'AWS_STORAGE_BUCKET_NAME' in os.environ:
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_AUTO_CREATE_BUCKET = True

    INSTALLED_APPS.append('storages')
    MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

if 'GS_BUCKET_NAME' in os.environ:
    GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME')
    GS_PROJECT_ID = os.getenv('GS_PROJECT_ID')
    GS_DEFAULT_ACL = 'publicRead'
    GS_AUTO_CREATE_BUCKET = True

    INSTALLED_APPS.append('storages')
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}
