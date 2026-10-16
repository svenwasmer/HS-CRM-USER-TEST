"""Read a HubSpot user's manager (the hs_manager property).

Usage: python get_manager.py <user_id> [--history]

  user_id    record ID of the user (get_user_id.py <email>)
  --history  list every recorded change to hs_manager, newest first, as
             "<timestamp>  <value>  <source type>  <source id>". An empty value
             is shown as (none). Changes that did not alter the value are not
             recorded by HubSpot.

Without --history, prints the manager's internal user ID, or an empty line if
no manager is set. Requires the crm.objects.users.read scope.
"""

import sys
from hs_common import BASE, USERS_OBJECT, headers, check, session

args = [a for a in sys.argv[1:] if a != "--history"]
history = "--history" in sys.argv[1:]
if len(args) != 1:
    sys.exit("Usage: get_manager.py <user_id> [--history]\n"
             "  user_id: record ID from get_user_id.py <email>\n"
             "  prints the manager's internal user ID, or an empty line if none is set\n"
             "  --history: print every recorded change to hs_manager, newest first")

user_id = args[0]
params = {"properties": "hs_manager"}
if history:
    params["propertiesWithHistory"] = "hs_manager"
res = check(session.get(
    f"{BASE}/crm/v3/objects/{USERS_OBJECT}/{user_id}",
    headers=headers(),
    params=params,
))

if not history:
    print(res["properties"].get("hs_manager") or "")
    sys.exit(0)

changes = (res.get("propertiesWithHistory") or {}).get("hs_manager", [])
if not changes:
    print("No hs_manager history recorded")
for c in changes:
    who = c.get("sourceId") or ""
    if c.get("updatedByUserId") is not None:
        who = f"{who} (user {c['updatedByUserId']})"
    print(f"{c['timestamp']}  {c['value'] or '(none)':<10}  {c['sourceType']}  {who}".rstrip())
