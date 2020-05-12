import json
import os
import re
from datetime import timedelta

import environ

from camac.utils import build_url

env = environ.Env()
ROOT_DIR = environ.Path(__file__) - 2

ENV_FILE = env.str("DJANGO_ENV_FILE", default=ROOT_DIR(".env"))
if os.path.exists(ENV_FILE):  # pragma: no cover
    environ.Env.read_env(ENV_FILE)

# We need to import the caluma settings after we merge os.environ with our
# local .env file otherwise caluma tries to get it's settings from it's own env
# file (which doesn't exist)

from caluma.settings.caluma import *  # noqa isort:skip

ENV = env.str("APPLICATION_ENV", default="production")
APPLICATION_NAME = env.str("APPLICATION")
APPLICATION_DIR = ROOT_DIR.path(APPLICATION_NAME)
FORM_CONFIG = json.loads(APPLICATION_DIR.file("form.json").read())


def default(default_dev=env.NOTSET, default_prod=env.NOTSET):
    """Environment aware default."""
    return default_prod if ENV == "production" else default_dev


SECRET_KEY = env.str("DJANGO_SECRET_KEY", default=default("uuuuuuuuuu"))
DEBUG = env.bool("DJANGO_DEBUG", default=default(True, False))
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=default(["*"]))
ENABLE_SILK = env.bool("DJANGO_ENABLE_SILK", default=False)

DEMO_MODE = env.bool("DEMO_MODE", default=False)

# Apache swallows info about HTTPS request, leading to issues with FileFields
# See https://docs.djangoproject.com/en/2.2/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.postgres",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    # Caluma and it's dependencies:
    "caluma.caluma_core.apps.DefaultConfig",
    "caluma.caluma_user.apps.DefaultConfig",
    "caluma.caluma_form.apps.DefaultConfig",
    "caluma.caluma_workflow.apps.DefaultConfig",
    "caluma.caluma_data_source.apps.DefaultConfig",
    "graphene_django",
    "localized_fields",
    "psqlextra",
    "simple_history",
    # Camac and it's dependencies
    "drf_yasg",
    "camac.core.apps.DefaultConfig",
    "camac.user.apps.DefaultConfig",
    "camac.instance.apps.DefaultConfig",
    "camac.document.apps.DefaultConfig",
    "camac.circulation.apps.DefaultConfig",
    "camac.notification.apps.DefaultConfig",
    "camac.responsible.apps.DefaultConfig",
    "camac.file.apps.DefaultConfig",
    "camac.applicants.apps.DefaultConfig",
    "camac.auditlog.apps.DefaultConfig",
    "camac.tags.apps.DefaultConfig",
    "camac.objection.apps.DefaultConfig",
    "camac.echbern.apps.EchbernConfig",
    "sorl.thumbnail",
    "django_clamd",
    "reversion",
    "rest_framework_xml",
    "gisbern",
]

if DEBUG:
    INSTALLED_APPS.append("django_extensions")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "camac.user.middleware.GroupMiddleware",
    "camac.middleware.LoggingMiddleware",
    "reversion.middleware.RevisionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]


ROOT_URLCONF = "camac.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ]
        },
    }
]

WSGI_APPLICATION = "camac.wsgi.application"

# Application specific settings
# an application is defined by the customer e.g. uri, schwyz, etc.

APPLICATIONS = {
    "demo": {
        # Mapping between camac role and instance permission.
        "ROLE_PERMISSIONS": {
            # Commonly used roles
            "Applicant": "applicant",
            "Municipality": "municipality",
            "Administration Leitbehörde": "municipality",
            "Service": "service",
            "Reader": "reader",
            "Canton": "canton",
            "PublicReader": "public_reader",
            "Support": "support",
        },
        "IS_MULTILINGUAL": False,
        "NOTIFICATIONS": {"SUBMIT": None, "APPLICANT": {"NEW": None, "EXISTING": None}},
        "PUBLICATION_DURATION": timedelta(days=30),
        "FORM_BACKEND": "camac-ng",
        "WORKFLOW_ITEMS": {
            "SUBMIT": None,
            "INSTANCE_COMPLETE": None,
            "PUBLICATION": None,
            "START_CIRC": None,
        },
        "PAPER": {
            "ALLOWED_ROLES": {"DEFAULT": []},
            "ALLOWED_SERVICE_GROUPS": {"DEFAULT": []},
        },
        "GROUP_RENAME_ON_SERVICE_RENAME": True,
        "SERVICE_UPDATE_ALLOWED_ROLES": [
            "Administration Leitbehörde"
        ],  # if unset, all are allowed
    },
    "kt_schwyz": {
        "ROLE_PERMISSIONS": {
            "Gemeinde": "municipality",
            "Gemeinde Sachbearbeiter": "municipality",
            "Fachstelle": "service",
            "Fachstelle Sachbearbeiter": "service",
            "Kanton": "canton",
            "Lesezugriff": "reader",
            "Publikation": "public_reader",
        },
        "NOTIFICATIONS": {
            "SUBMIT": "gesuchseingang",
            "APPLICANT": {
                "NEW": "gesuchsbearbeitungs-einladung-neu",
                "EXISTING": "gesuchsbearbeitungs-einladung-bestehend",
            },
            "PUBLICATION_PERMISSION": "publikation-einsehen",
        },
        "PUBLICATION_DURATION": timedelta(days=30),
        "IS_MULTILINGUAL": False,
        "FORM_BACKEND": "camac-ng",
        "COORDINATE_QUESTION": "punkte",
        "WORKFLOW_ITEMS": {
            "SUBMIT": 10,
            "INSTANCE_COMPLETE": 14,
            "PUBLICATION": 15,
            "START_CIRC": 44,
        },
        "QUESTIONS_WITH_OVERRIDE": [
            "bezeichnung",
            "bauherrschaft",
            "projektverfasser-planer",
            "grundeigentumerschaft",
        ],
        "INSTANCE_IDENTIFIER_FORM_ABBR": {
            "geschaeftskontrolle": "GK",
            "municipality": "GS",
            "bezirk": "BS",
            "canton": "KS",
            "astra": "PA",
            "esti": "PE",
            "bav": "PB",
            "vbs": "PV",
        },
    },
    "kt_bern": {
        "ROLE_PERMISSIONS": {
            "service-lead": "service",
            "service-clerk": "service",
            "service-readonly": "service",
            "service-admin": "service",
            "subservice": "service",
            "municipality-lead": "municipality",
            "municipality-clerk": "municipality",
            "municipality-readonly": "municipality",
            "municipality-admin": "municipality",
            "construction-control-lead": "municipality",
            "construction-control-clerk": "municipality",
            "construction-control-readonly": "municipality",
            "construction-control-admin": "municipality",
            "support": "support",
        },
        "NOTIFICATIONS": {
            "SUBMIT": [
                {
                    "template_slug": "00-empfang-anfragebaugesuch-gesuchsteller",
                    "recipient_types": ["applicant"],
                },
                {
                    "template_slug": "00-empfang-anfragebaugesuch-behorden",
                    "recipient_types": ["leitbehoerde"],
                },
            ],
            "REPORT": [
                {
                    "template_slug": "11-meldung-selbstdeklaration-gesuchsteller",
                    "recipient_types": ["applicant"],
                },
                {
                    "template_slug": "11-meldung-selbstdeklaration-baukontrolle",
                    "recipient_types": ["construction_control"],
                },
            ],
            "FINALIZE": [
                {
                    "template_slug": "13-meldung-termine-pflichtkontrollen-baukontrolle",
                    "recipient_types": ["construction_control"],
                }
            ],
            "APPLICANT": {
                "NEW": "gesuchsbearbeitungs-einladung-neu",
                "EXISTING": "gesuchsbearbeitungs-einladung-bestehend",
            },
        },
        "PUBLICATION_DURATION": timedelta(),
        "IS_MULTILINGUAL": True,
        "FORM_BACKEND": "caluma",
        "CALUMA": {"FORM_PERMISSIONS": ["main", "sb1", "sb2", "nfd"]},
        "DEMO_MODE_GROUPS": [
            20003,
            20006,
            20096,
            20144,
            20069,
            22648,
            20165,
            22642,
            20291,
        ],  # DE
        # "DEMO_MODE_GROUPS": [22274, 22271, 20099, 20078, 23248],  # FR
        "ACTIVE_SERVICE_FILTERS": {"service__service_group__pk__in": [2, 20000]},
        "ACTIVE_BAUKONTROLLE_FILTERS": {"service__service_group__pk": 3},
        "PDF": {
            "SECTION": {
                "MAIN": {"DEFAULT": 1, "PAPER": 13},
                "SB1": {"DEFAULT": 6, "PAPER": 10},
                "SB2": {"DEFAULT": 5, "PAPER": 11},
            }
        },
        "PAPER": {
            "ALLOWED_ROLES": {
                "SB1": [5, 20005],
                "SB2": [5, 20005],
                "DEFAULT": [3, 20004],
            },
            "ALLOWED_SERVICE_GROUPS": {"SB1": [3], "SB2": [3], "DEFAULT": [2, 20000]},
        },
        "DOCUMENT_MERGE_SERVICE": {
            "baugesuch": {
                "forms": [
                    "baugesuch",
                    "baugesuch-mit-uvp",
                    "baugesuch-generell",
                    "vorabklaerung-vollstaendig",
                ],
                "template": "2-level",
                "allgemeine_info": "1-allgemeine-informationen",
                "personalien": "personalien",
                "people_sources": {
                    "personalien-gesuchstellerin": {
                        "familyName": "name-gesuchstellerin",
                        "givenName": "vorname-gesuchstellerin",
                    },
                    "personalien-vertreterin-mit-vollmacht": {
                        "familyName": "name-vertreterin",
                        "givenName": "vorname-vertreterin",
                    },
                    "personalien-grundeigentumerin": {
                        "familyName": "name-grundeigentuemerin",
                        "givenName": "vorname-grundeigentuemerin",
                    },
                    "personalien-gebaudeeigentumerin": {
                        "familyName": "name-gebaeudeeigentuemerin",
                        "givenName": "vorname-gebaeudeeigentuemerin",
                    },
                    "personalien-projektverfasserin": {
                        "familyName": "name-projektverfasserin",
                        "givenName": "vorname-projektverfasserin",
                    },
                },
                "exclude_slugs": [
                    "papierdossier",
                    "projektaenderung",
                    "8-freigabequittung",
                ],
            },
            "vorabklaerung-einfach": {
                "forms": ["vorabklaerung-einfach"],
                "template": "1-level",
                "allgemeine_info": "allgemeine-informationen-vorabklaerung-form",
                "givenName": "vorname-gesuchstellerin-vorabklaerung",
                "familyName": "name-gesuchstellerin-vorabklaerung",
                "exclude_slugs": [
                    "papierdossier",
                    "projektaenderung",
                    "freigabequittung-vorabklaerung-form",
                    "dokumente-vorabklaerung-form",
                ],
            },
            "selbstdeklaration": {
                "forms": ["sb1", "sb2"],
                "template": "1-level",
                "exclude_slugs": [
                    "papierdossier",
                    "freigabequittung-sb1",
                    "freigabequittung-sb2",
                    "dokumente-sb1",
                    "dokumente-sb2",
                ],
            },
        },
        "GROUP_RENAME_ON_SERVICE_RENAME": True,
        "SERVICE_UPDATE_ALLOWED_ROLES": [
            "municipality-admin",
            "service-admin",
            "construction-control-admin",
        ],
        "SUGGESTIONS": [
            (
                "art-versickerung-dach",
                "art-versickerung-dach-oberflaechengewaesser",
                [20063],
            ),
            (
                "art-versickerung-platz",
                "art-versickerung-platz-oberflachengewasser",
                [20063],
            ),
            (
                "ausnahme-im-sinne-von-artikel-64-kenv",
                "ausnahme-im-sinne-von-artikel-64-kenv-ja",
                [20046],
            ),
            ("aussenlaerm", "aussenlaerm-ja", [20054]),
            (
                "bau-im-wald-oder-innerhalb-von-30-m-abstand",
                "bau-im-wald-oder-innerhalb-von-30-m-abstand-ja",
                [20048],
            ),
            ("baubeschrieb", "baubeschrieb-erweiterung-anbau", [20068, 20055]),
            ("baubeschrieb", "baubeschrieb-neubau", [20055]),
            ("baubeschrieb", "baubeschrieb-technische-anlage", [20055]),
            ("baubeschrieb", "baubeschrieb-tiefbauanlage", [20068]),
            ("baubeschrieb", "baubeschrieb-um-ausbau", [20055, 20068]),
            ("baubeschrieb", "baubeschrieb-umnutzung", [20055]),
            ("baugruppe-bauinventar", "baugruppe-bauinventar-ja", [20043]),
            (
                "bauten-oder-pfaehlen-im-grundwasser",
                "bauten-oder-pfaehlen-im-grundwasser-ja",
                [20050],
            ),
            ("belasteter-standort", "belasteter-standort-ja", [20050]),
            ("besondere-brandrisiken", "besondere-brandrisiken-ja", [20057]),
            ("brandbelastung", "brandbelastung-ja", [20057]),
            (
                "eigenstaendiger-grossverbraucher",
                "eigenstaendiger-grossverbraucher-ja",
                [20046],
            ),
            ("erhaltenswert", "erhaltenswert-ja", [20043]),
            ("feuerungsanlagen", "feuerungsanlagen-holzfeuerungen", [20057]),
            (
                "feuerungsanlagen",
                "feuerungsanlagen-ol-oder-gasfeuerungen-350-kw",
                [20057],
            ),
            (
                "feuerungsanlagen",
                "feuerungsanlagen-pellet-schnitzelfeuerungsanlage",
                [20055],
            ),
            (
                "feuerungsanlagen",
                "feuerungsanlagen-pellet-schnitzelfeuerungsanlage",
                [20054],
            ),
            (
                "feuerungsanlagen",
                "feuerungsanlagen-pellet-schnitzelfeuerungsanlage",
                [20057],
            ),
            (
                "gebiet-mit-archaeologischen-objekten",
                "gebiet-mit-archaeologischen-objekten-ja",
                [20043],
            ),
            ("gebiet-mit-naturgefahren", "gebiet-mit-naturgefahren-ja", [20049]),
            ("gefahrenstufe", "gefahrenstufe-blau", [20049]),
            ("gefahrenstufe", "gefahrenstufe-rot", [20049]),
            ("gefahrenstufe", "gefahrenstufe-unbestimmt", [20049]),
            ("gefaehrliche-stoffe", "gefaehrliche-stoffe-ja", [20055]),
            (
                "gentechnisch-veraenderte-organismen",
                "gentechnisch-veraenderte-organismen-ja",
                [20060],
            ),
            (
                "geplante-anlagen",
                "geplante-anlagen-solar-oder-photovoltaik-anlage",
                [20054],
            ),
            ("gewaesserschutzbereich", "gewaesserschutzbereich-zu", [20050]),
            ("grundwasserschutzzonen", "grundwasserschutzzonen-s1", [20050]),
            ("grundwasserschutzzonen", "grundwasserschutzzonen-s2sh", [20050]),
            ("grundwasserschutzzonen", "grundwasserschutzzonen-s3sm", [20050]),
            (
                "ist-das-vorhaben-energierelevant",
                "ist-das-vorhaben-energierelevant-ja",
                [20046],
            ),
            (
                "ist-durch-das-bauvorhaben-boden-betroffen",
                "ist-durch-das-bauvorhaben-boden-betroffen-ja",
                [20050],
            ),
            (
                "ist-mit-bauabfaellen-zu-rechnen",
                "ist-mit-bauabfaellen-zu-rechnen-ja",
                [20050],
            ),
            ("k-objekt", "k-objekt-ja", [20043]),
            (
                "klassierung-der-taetigkeit",
                "klassierung-der-taetigkeit-klasse-3",
                [20055],
            ),
            (
                "klassierung-der-taetigkeit",
                "klassierung-der-taetigkeit-klasse-4",
                [20055],
            ),
            (
                "landwirtschaftliches-vorhaben-mit-ableitung",
                "landwirtschaftliches-vorhaben-mit-ableitung-ja",
                [20050],
            ),
            ("maschinelle-arbeitsmittel", "maschinelle-arbeitsmittel-ja", [20055]),
            (
                "maschinen-aus-den-folgenden-kategorien",
                "maschinen-aus-den-folgenden-kategorien-erzeugung",
                [20055],
            ),
            (
                "maschinen-aus-den-folgenden-kategorien",
                "maschinen-aus-den-folgenden-kategorien-reinigung",
                [20055],
            ),
            (
                "maschinen-aus-den-folgenden-kategorien",
                "maschinen-aus-den-folgenden-kategorien-strom",
                [20055],
            ),
            (
                "maschinen-aus-den-folgenden-kategorien",
                "maschinen-aus-den-folgenden-kategorien-transport",
                [20055],
            ),
            (
                "maschinen-aus-den-folgenden-kategorien",
                "maschinen-aus-den-folgenden-kategorien-werkhoefe",
                [20055],
            ),
            ("naturschutz", "naturschutz-ja", [20065]),
            ("nutzungsart", "nutzungsart-andere", [20054, 20055]),
            ("nutzungsart", "nutzungsart-dienstleistung", [20054, 20055]),
            ("nutzungsart", "nutzungsart-gastgewerbe", [20054, 20055]),
            ("nutzungsart", "nutzungsart-gewerbe", [20054, 20055, 20074]),
            ("nutzungsart", "nutzungsart-industrie", [20054, 20055, 20074]),
            ("nutzungsart", "nutzungsart-lager", [20054, 20055]),
            ("nutzungsart", "nutzungsart-landwirtschaft", [20054, 20055, 20074]),
            ("nutzungsart", "nutzungsart-verkauf", [20054, 20055]),
            ("organismen-in-anlage", "organismen-in-anlage-andere", [20055]),
            ("organismen-in-anlage", "organismen-in-anlage-bakterien", [20055]),
            ("organismen-in-anlage", "organismen-in-anlage-viren", [20055]),
            ("rrb", "rrb-ja", [20043]),
            ("schuetzenswert", "schuetzenswert-ja", [20043]),
            (
                "sind-belange-des-gewasserschutzes-betroffen",
                "sind-belange-des-gewasserschutzes-betroffen-ja",
                [20050],
            ),
            ("versickerung", "versickerung-nein", [20063]),
            ("verunreinigte-abluft", "verunreinigte-abluft-ja", [20054]),
            (
                "verwendungszweck-der-anlage",
                "verwendungszweck-der-anlage-andere",
                [20055],
            ),
            (
                "verwendungszweck-der-anlage",
                "verwendungszweck-der-anlage-diagnostik",
                [20055],
            ),
            (
                "verwendungszweck-der-anlage",
                "verwendungszweck-der-anlage-forschung",
                [20055],
            ),
            (
                "verwendungszweck-der-anlage",
                "verwendungszweck-der-anlage-gewaechshaus",
                [20055],
            ),
            (
                "verwendungszweck-der-anlage",
                "verwendungszweck-der-anlage-produktion",
                [20055],
            ),
            (
                "verwendungszweck-der-anlage",
                "verwendungszweck-der-anlage-tieranlage",
                [20055],
            ),
            (
                "verwendungszweck-der-anlage",
                "verwendungszweck-der-anlage-unterricht",
                [20055],
            ),
            ("was-fuer-ein-vorhaben", "was-fuer-ein-vorhaben-andere", [20055]),
            ("was-fuer-ein-vorhaben", "was-fuer-ein-vorhaben-grossraumbueros", [20055]),
            ("was-fuer-ein-vorhaben", "was-fuer-ein-vorhaben-spitaeler", [20055]),
            (
                "was-fuer-ein-vorhaben",
                "was-fuer-ein-vorhaben-verkaufsgeschaefte",
                [20055],
            ),
            (
                "wassergefaehrdende-explosive-stoffe",
                "wassergefaehrdende-explosive-stoffe-ja",
                [20050, 20060],
            ),
            (
                "welche-art-vorhaben",
                "welche-art-vorhaben-erstellung-aussenraum",
                [20068],
            ),
            (
                "welche-art-vorhaben",
                "welche-art-vorhaben-fischhaltung-aquakulturanlage",
                [20050, 20051, 20052, 20053, 20063],
            ),
            ("welche-waermepumpen", "welche-waermepumpen-boden-untergrund", [20053]),
            ("welche-waermepumpen", "welche-waermepumpen-luft", [20054]),
            ("welche-waermepumpen", "welche-waermepumpen-wasser", [20053, 20063]),
            (
                "werden-brandschutzabstaende-unterschritten",
                "werden-brandschutzabstande-unterschritten-ja",
                [20057],
            ),
            ("werden-siloanlagen-erstellt", "werden-siloanlagen-erstellt-ja", [20055]),
            ("wildtierschutz", "wildtierschutz-ja", [20064]),
        ],
    },
    "kt_uri": {"FORM_BACKEND": "camac"},
}

APPLICATION = APPLICATIONS.get(APPLICATION_NAME, {})

PUBLIC_BASE_URL = build_url(
    env.str("DJANGO_PUBLIC_BASE_URL", default="http://caluma-portal.local")
)

INTERNAL_BASE_URL = build_url(
    env.str("DJANGO_INTERNAL_BASE_URL", default="http://camac-ng.local")
)

PUBLIC_INSTANCE_URL_TEMPLATE = env.str(
    "DJANGO_PUBLIC_INSTANCE_URL_TEMPLATE",
    default=build_url(PUBLIC_BASE_URL, "/instances/{instance_id}"),
)
INTERNAL_INSTANCE_URL_TEMPLATE = env.str(
    "DJANGO_INTERNAL_INSTANCE_URL_TEMPLATE",
    default=build_url(
        INTERNAL_BASE_URL,
        "/index/redirect-to-instance-resource/instance-id/{instance_id}",
    ),
)

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(asctime)s] %(message)s",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {"django": {"handlers": ["console", "mail_admins"], "level": "INFO"}},
}

REQUEST_LOGGING_METHODS = env.list(
    "DJANGO_REQUEST_LOGGING_METHODS",
    default=default(["POST", "PUT", "PATCH", "DELETE"], []),
)
REQUEST_LOGGING_CONTENT_TYPES = env.list(
    "DJANGO_REQUEST_LOGGING_CONTENT_TYPES", default=["application/vnd.api+json"]
)

# Managing files

MEDIA_ROOT = env.str("DJANGO_MEDIA_ROOT", default=default(ROOT_DIR("media")))
TEMPFILE_DOWNLOAD_PATH = env.str(
    "DJANGO_TEMPFILE_DOWNLOAD_PATH", default="/tmp/camac/tmpfiles"
)
TEMPFILE_DOWNLOAD_URL = env.str("DJANGO_TEMPFILE_DOWNLOAD_URL", default="/zips")
# in seconds
TEMPFILE_RETENTION_TIME = env.int(
    "DJANGO_TEMPFILE_RETENTION_TIME", default=(60 * 60 * 24)
)

STATIC_ROOT = ROOT_DIR("staticfiles")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

DEFAULT_FILE_STORAGE = env.str(
    "DJANGO_DEFAULT_FILE_STORAGE", default="django.core.files.storage.FileSystemStorage"
)
FILE_UPLOAD_PERMISSIONS = env.int("FILE_UPLOAD_PERMISSIONS", default=0o644)

THUMBNAIL_ENGINE = "sorl.thumbnail.engines.convert_engine.Engine"

DEFAULT_DOCUMENT_MIMETYPES = env.list(
    "DJANGO_DEFAULT_DOCUMENT_MIMETYPES",
    default=["image/png", "image/jpeg", "application/pdf"],
)
ALLOWED_DOCUMENT_MIMETYPES = env.list(
    "DJANGO_ALLOWED_DOCUMENT_MIMETYPES",
    default=[
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        "application/xml",
        "image/gif",
        "image/jpeg",
        "image/png",
        "image/tiff",
        "text/plain",
    ],
)

# Unoconv webservice
# https://github.com/zrrrzzt/tfk-api-unoconv

UNOCONV_URL = env.str("DJANGO_UNOCONV_URL", default="http://localhost:3000")


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "camac.core.postgresql_dbdefaults.psqlextra",
        "NAME": env.str("DATABASE_NAME", default=APPLICATION_NAME),
        "USER": env.str("DATABASE_USER", default="camac"),
        "PASSWORD": env.str("DATABASE_PASSWORD", default=default("camac")),
        "HOST": env.str("DATABASE_HOST", default="localhost"),
        "PORT": env.str("DATABASE_PORT", default=""),
    }
}

# Sequence ranges to be used for each developer. Note: NEVER EVER
# EVER change this without talking to the affected developers. New
# developers should just be appended instead (which is safe).
SEQUENCE_NAMESPACES_SIZE = 10000
SEQUENCE_NAMESPACES = {}


# Cache
# https://docs.djangoproject.com/en/1.11/ref/settings/#caches

CACHES = {
    "default": {
        "BACKEND": env.str(
            "DJANGO_CACHE_BACKEND",
            default="django.core.cache.backends.memcached.MemcachedCache",
        ),
        "LOCATION": env.str("DJANGO_CACHE_LOCATION", default="127.0.0.1:11211"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LOCALE_NAME = "de_CH"
LANGUAGE_CODE = "de"
LANGUAGES = [("de", "German"), ("fr", "French")]
TIME_ZONE = "Europe/Zurich"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = (os.path.join(ROOT_DIR, "locale"),)


AUTH_PASSWORT_SALT = "ds5fsdFd763znsPO"
AUTH_USER_MODEL = "user.User"

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "rest_framework_json_api.exceptions.exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework_json_api.pagination.JsonApiPageNumberPagination",
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework_json_api.parsers.JSONParser",
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework_json_api.renderers.JSONRenderer",
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "camac.user.permissions.IsGroupMember",
        "camac.user.permissions.ViewPermissions",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "camac.user.authentication.JSONWebTokenKeycloakAuthentication",
    ),
    "DEFAULT_METADATA_CLASS": "rest_framework_json_api.metadata.JSONAPIMetadata",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "ORDERING_PARAM": "sort",
    "TEST_REQUEST_RENDERER_CLASSES": (
        "rest_framework_json_api.renderers.JSONRenderer",
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.MultiPartRenderer",
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "vnd.api+json",
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

JSON_API_FORMAT_FIELD_NAMES = "dasherize"
JSON_API_FORMAT_TYPES = "dasherize"
JSON_API_PLURALIZE_TYPES = True

# Clamav service

CLAMD_USE_TCP = True
CLAMD_TCP_ADDR = env.str("DJANGO_CLAMD_TCP_ADDR", default="localhost")
CLAMD_ENABLED = env.bool("DJANGO_CLAMD_ENABLED", default=True)


# Keycloak service

KEYCLOAK_URL = build_url(
    env.str("KEYCLOAK_URL", default="http://camac-ng-keycloak.local/auth/"),
    trailing=True,
)
KEYCLOAK_REALM = env.str("KEYCLOAK_REALM", default="ebau")
KEYCLOAK_CLIENT = env.str("KEYCLOAK_CLIENT", default="camac")

KEYCLOAK_OIDC_TOKEN_URL = build_url(
    KEYCLOAK_URL, f"/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
)

OIDC_BEARER_TOKEN_REVALIDATION_TIME = env.int(
    "OIDC_BEARER_TOKEN_REVALIDATION_TIME", default=10
)
REGISTRATION_URL = env.str(
    "DJANGO_REGISTRATION_URL",
    default=build_url(
        KEYCLOAK_URL,
        f"/realms/{KEYCLOAK_REALM}/login-actions/registration?client_id={KEYCLOAK_CLIENT}",
    ),
)

# Email definition

DEFAULT_FROM_EMAIL = env.str(
    "DJANGO_DEFAULT_FROM_EMAIL", default("webmaster@localhost")
)

SERVER_EMAIL = env.str("DJANGO_SERVER_EMAIL", default("root@localhost"))

EMAIL_HOST = env.str("DJANGO_EMAIL_HOST", default("localhost"))
EMAIL_PORT = env.str("DJANGO_EMAIL_PORT", 25)

EMAIL_HOST_USER = env.str("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env.str("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env.str("DJANGO_EMAIL_USE_TLS", False)

EMAIL_PREFIX_SUBJECT = env.str("EMAIL_PREFIX_SUBJECT", default("[eBau Test]: ", ""))
EMAIL_PREFIX_BODY = env.str(
    "EMAIL_PREFIX_BODY",
    default(
        (
            "Hinweis: Diese Nachricht wurde von einem Testsystem versendet.\n"
            "Es dient nur zu Testzwecken und kann ignoriert werden\n\n"
        ),
        "",
    ),
)


# Merge definition
MERGE_DATE_FORMAT = env.str("DJANGO_MERGE_DATE_FORMAT", "%d.%m.%Y")
MERGE_ANSWER_PERIOD = env.int("DJANGO_MERGE_ANSWER_PERIOD", 20)


def parse_admins(admins):
    """
    Parse env admins to django admins.

    Example of DJANGO_ADMINS environment variable:
    Test Example <test@example.com>,Test2 <test2@example.com>
    """
    result = []
    for admin in admins:
        match = re.search(r"(.+) \<(.+@.+)\>", admin)
        if not match:
            raise environ.ImproperlyConfigured(
                'In DJANGO_ADMINS admin "{0}" is not in correct '
                '"Firstname Lastname <email@example.com>"'.format(admin)
            )
        result.append((match.group(1), match.group(2)))
    return result


ADMINS = parse_admins(env.list("DJANGO_ADMINS", default=[]))

# GIS API (Kt. BE)
GIS_BASE_URL = build_url(env.str("GIS_BASE_URL", "https://www.geoservice.apps.be.ch"))
GIS_API_USER = env.str("GIS_API_USER", "")
GIS_API_PASSWORD = env.str("GIS_API_PASSWORD", "")

GIS_SKIP_BOOLEAN_LAYERS = env.list("GIS_SKIP_BOOLEAN_LAYERS", default=[])

GIS_SKIP_SPECIAL_LAYERS = env.list("GIS_SKIP_SPECIAL_LAYERS", default=[])

DOCUMENT_MERGE_SERVICE_URL = build_url(
    env.str("DOCUMENT_MERGE_SERVICE_URL", "http://document-merge-service:8000/api/v1/")
)

ECH_API = env.bool("ECH_API", default=True)

# Swagger settings
SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "DEEP_LINKING": True,
    "SECURITY_DEFINITIONS": {
        "oauth2": {
            "type": "oauth2",
            "tokenUrl": KEYCLOAK_OIDC_TOKEN_URL,
            "flow": "application",
            "scopes": {},
        }
    },
    "DEFAULT_PAGINATOR_INSPECTORS": [
        "camac.swagger.schema.DjangoRestJsonApiResponsePagination",
        "drf_yasg.inspectors.CoreAPICompatInspector",
    ],
    "DEFAULT_FIELD_INSPECTORS": [
        "camac.swagger.schema.ModelSerializerInspector",
        "drf_yasg.inspectors.CamelCaseJSONFilter",
        "drf_yasg.inspectors.ReferencingSerializerInspector",
        "drf_yasg.inspectors.RelatedFieldInspector",
        "drf_yasg.inspectors.ChoiceFieldInspector",
        "drf_yasg.inspectors.FileFieldInspector",
        "drf_yasg.inspectors.DictFieldInspector",
        "drf_yasg.inspectors.HiddenFieldInspector",
        "drf_yasg.inspectors.RecursiveFieldInspector",
        "drf_yasg.inspectors.SerializerMethodFieldInspector",
        "drf_yasg.inspectors.SimpleFieldInspector",
        "drf_yasg.inspectors.StringDefaultFieldInspector",
    ],
}

# Schwyz Publication
PUBLICATION_API_URL = build_url(
    env.str("PUBLICATION_API_URL", "https://amtsblatt-test.webtech.ch/api/v1/baugesuch")
)
PUBLICATION_API_USER = env.str("PUBLICATION_API_USER", "")
PUBLICATION_API_PASSWORD = env.str("PUBLICATION_API_PASSWORD", "")

if ENABLE_SILK:  # pragma: no cover
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.extend(
        [
            "django.contrib.sessions.middleware.SessionMiddleware",
            "silk.middleware.SilkyMiddleware",
        ]
    )

    SILKY_AUTHENTICATION = False
    SILKY_AUTHORISATION = False
    SILKY_META = True
