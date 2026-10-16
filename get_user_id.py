"""Look up a HubSpot user's ID by email address.

Usage: python get_user_id.py <email> [--internal]

HubSpot users have two IDs:
  * record ID (default output): identifies the user record in this account.
    Use it as the <user_id> argument of get_manager.py and set_manager.py.
  * internal user ID (--internal): identifies the user across HubSpot
    accounts. This is the value stored in a user's hs_manager property, so use
    it as the <manager_id> argument of set_manager.py.

Prints the ID on stdout so it can be captured, e.g. USER=$(python get_user_id.py a@b.com).
Exits non-zero if no user has that email.
"""

import sys
from hs_common import BASE, USERS_OBJECT, headers, check, session

args = [a for a in sys.argv[1:] if a != "--internal"]
internal = "--internal" in sys.argv[1:]
if len(args) != 1:
    sys.exit("Usage: get_user_id.py <email> [--internal]\n"
             "  default: record ID (the user_id argument of get_manager/set_manager)\n"
             "  --internal: internal user ID (the value hs_manager stores; use as manager_id)")
email = args[0]
body = {
    "filterGroups": [{"filters": [{"propertyName": "hs_email", "operator": "EQ", "value": email}]}],
    "properties": ["hs_email", "hs_internal_user_id"],
    "limit": 1,
}
res = check(session.post(f"{BASE}/crm/v3/objects/{USERS_OBJECT}/search", headers=headers(), json=body))
results = res.get("results", [])
if not results:
    sys.exit(f"No user found for {email}")
user = results[0]
print(user["properties"]["hs_internal_user_id"] if internal else user["id"])
