# HubSpot user manager scripts

Small command-line scripts to look up a HubSpot user, read their manager, and set or clear it. They call the CRM Users API (object type `0-115`) and work on the `hs_manager` property.

| Script | Purpose |
|---|---|
| `get_user_id.py` | Find a user's ID from their email |
| `get_manager.py` | Read a user's manager, or its change history |
| `set_manager.py` | Set or clear a user's manager |
| `hs_common.py` | Shared helpers (base URL, session, auth headers, error handling) |

`hs_client.py` is left over from an older project. It imports `src.config`, which doesn't exist here, and nothing uses it.

## Setup

1. Create a HubSpot private app (Development -> Keys -> Service Keys) and give it the scopes `crm.objects.users.read` and `crm.objects.users.write`.
2. Put its token in a `.env` file in this folder (already git-ignored):
   ```
   HUBSPOT_TOKEN=your-token-here
   ```
3. Install dependencies:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Two kinds of user ID

This is the most common source of mistakes.

| | Record ID | Internal user ID |
|---|---|---|
| Property | `hs_object_id` / API `id` | `hs_internal_user_id` |
| Scope | This HubSpot account only | The same user across accounts |
| Example | `527055195754` | `44702364` |
| Used for | Choosing which user to read or update (`<user_id>`) | The value stored in `hs_manager` (`<manager_id>`) |

`get_user_id.py <email>` returns the record ID. `get_user_id.py <email> --internal` returns the internal user ID. The user you're updating is identified by record ID, and the manager you assign is identified by internal user ID. Passing a record ID as the manager is wrong.

## Usage

Look up IDs:

```
python get_user_id.py someone@example.com             # record ID
python get_user_id.py manager@example.com --internal  # internal user ID
```

Read a manager:

```
python get_manager.py <user_id>             # manager's internal user ID, or an empty line if none
python get_manager.py <user_id> --history   # every recorded change, newest first
```

History output looks like this:

```
2026-10-16T10:48:58.038Z  87821911    INTEGRATION  50505123
2026-10-16T10:48:56.942Z  (none)      INTEGRATION  50505123
2026-10-15T15:36:58.839Z  87821911    API  userId:87821911 (user 87821911)
```

Writing the value a user already has isn't recorded.

Set or clear a manager:

```
python set_manager.py <user_id> <manager_id>   # set
python set_manager.py <user_id> --clear        # remove
```

Full example, making Danial report to Sven:

```
USER=$(python get_user_id.py danial_seller@demospot.org)
MGR=$(python get_user_id.py swasmer@hubspot.com --internal)
python get_manager.py $USER        # check the current value first
python set_manager.py $USER $MGR
python get_manager.py $USER --history
```

`set_manager.py` writes to the live account. Check the IDs before you run it.

## Notes

- The manager must be an active, non-partner user in the account.
- Property history for users isn't shown in the HubSpot UI. Use `get_manager.py --history`.
- Scripts exit non-zero with a message on any HTTP error, and print a usage message when arguments are missing.
- `hs_common.py` mounts a session that drops Python 3.13+'s strict X.509 check. This fixes `CERTIFICATE_VERIFY_FAILED ... self-signed certificate in certificate chain` errors behind TLS-inspecting proxies. Certificate and hostname verification stay on.
- The scripts use the legacy `/crm/v3` endpoints. HubSpot's latest docs use date-versioned paths (`/crm/objects/2026-09/users`). The legacy paths still work.
