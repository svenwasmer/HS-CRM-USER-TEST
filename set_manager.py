"""Set or clear a HubSpot user's manager (the hs_manager property).

Usage: python set_manager.py <user_id> <manager_id | --clear>

  user_id     record ID of the user to update (get_user_id.py <email>)
  manager_id  the manager's INTERNAL user ID (get_user_id.py <email> --internal),
              not their record ID; hs_manager stores internal user IDs
  --clear     remove the user's manager

The manager must be an active, non-partner user in the account. Prints the
resulting hs_manager value. Writes to the live account, so check IDs first.
Requires the crm.objects.users.write scope.
"""

import sys
from hs_common import BASE, USERS_OBJECT, headers, check, session

if len(sys.argv) != 3:
    sys.exit("Usage: set_manager.py <user_id> <manager_id | --clear>\n"
             "  user_id: record ID from get_user_id.py <email>\n"
             "  manager_id: internal user ID from get_user_id.py <email> --internal\n"
             "  --clear: remove the user's manager")

user_id, manager = sys.argv[1], sys.argv[2]
manager_id = "" if manager == "--clear" else manager
res = check(session.patch(
    f"{BASE}/crm/v3/objects/{USERS_OBJECT}/{user_id}",
    headers=headers(),
    json={"properties": {"hs_manager": manager_id}},
))
print(f"hs_manager for {user_id} is now {res['properties'].get('hs_manager') or '(none)'}")
