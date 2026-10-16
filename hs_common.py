"""Shared helpers for the HubSpot user-manager scripts.

Provides the API base URL, the Users object type ID, an HTTP session that works
behind TLS-inspecting proxies, auth headers, and response checking.

Reads HUBSPOT_TOKEN from the environment or a local .env file. The token must
be a private app token with the crm.objects.users.read and
crm.objects.users.write scopes.
"""

import os
import ssl
import sys
import requests
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv
load_dotenv()

#: HubSpot API root.
BASE = "https://api.hubapi.com"
#: CRM object type ID for Users.
USERS_OBJECT = "0-115"

class RelaxedSSLAdapter(HTTPAdapter):
    """Keep certificate verification but drop Python 3.13+'s VERIFY_X509_STRICT.

    Python 3.13+ rejects some certificate chains (for example from corporate
    TLS-inspecting proxies) that older versions accept. Certificate and
    hostname verification stay on; only the strict X.509 profile check is off.
    """

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.verify_flags &= ~ssl.VERIFY_X509_STRICT
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)

#: Shared session; all scripts send their requests through it.
session = requests.Session()
session.mount("https://", RelaxedSSLAdapter())

def headers():
    """Return the auth and content-type headers for a HubSpot API request.

    Exits with a message if HUBSPOT_TOKEN is not set.
    """
    token = os.environ.get("HUBSPOT_TOKEN")
    if not token:
        sys.exit("Set HUBSPOT_TOKEN env var")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def check(r):
    """Return the decoded JSON body of response `r`.

    Exits with the HTTP status and response text if the request failed.
    """
    if not r.ok:
        sys.exit(f"HTTP {r.status_code}: {r.text}")
    return r.json()
