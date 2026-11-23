"""First-boot setup for the Railway template (runs before the API starts, as appuser).

* Creates the first super admin from ADMIN_EMAIL / ADMIN_PASSWORD when the
  database has no users yet, so a fresh deploy never has an open
  /api/v1/auth/init window and never uses upstream's demo accounts.
  It does nothing once any user exists: change passwords in the web UI.
* Points deployment.frontend_url / deployment.public_url at the Railway public
  URL (PUBLIC_URL), unless an admin has changed them in Admin > Settings.
* Trusts Railway's private network (IPv6 fd00::/8) as a proxy, so the API sees
  each visitor's own IP behind the web service instead of the proxy's.
"""

import asyncio
import os
import sys

from sqlalchemy import func, select

import models  # noqa: F401  (registers every table, as the API does)
from config import settings  # noqa: F401  (loads secrets the same way the API does)
from database import async_session, engine
from models.enterprise_config import EnterpriseConfig
from models.user import User, UserRole
from services.username_generator import generate_unique_username

UPSTREAM_TRUSTED = "172.16.0.0/12,10.0.0.0/8,192.168.0.0/16,127.0.0.1"
# The API listens on a dual-stack socket, so IPv4 peers on Railway's private
# network arrive as IPv4-mapped IPv6 (::ffff:10.x.x.x); fd00::/8 is its IPv6 range.
RAILWAY_TRUSTED = UPSTREAM_TRUSTED + ",::ffff:10.0.0.0/104,::ffff:172.16.0.0/108,::ffff:192.168.0.0/112,::ffff:127.0.0.1,::1,fd00::/8"
# Values this script wrote in earlier template versions: replaced, admin edits kept.
OUR_OLD_TRUSTED = {UPSTREAM_TRUSTED + ",fd00::/8"}
MARKER = "_railway.auto_public_url"


def log(msg: str) -> None:
    print(f"railway-bootstrap: {msg}", flush=True)


async def get_row(db, key):
    return (await db.execute(select(EnterpriseConfig).where(EnterpriseConfig.key == key))).scalar_one_or_none()


async def put(db, key, value):
    row = await get_row(db, key)
    if row is None:
        db.add(EnterpriseConfig(key=key, value=value))
    else:
        row.value = value


async def main() -> int:
    email = os.environ["ADMIN_EMAIL"].strip().lower()
    password = os.environ["ADMIN_PASSWORD"]
    public_url = os.environ.get("PUBLIC_URL", "").strip().rstrip("/")
    changed_keys = []

    async with async_session() as db:
        users = await db.scalar(select(func.count()).select_from(User)) or 0
        if users == 0:
            user = User(
                email=email,
                username=await generate_unique_username(email, db),
                name="Administrator",
                role=UserRole.super_admin,
            )
            user.set_password(password)
            db.add(user)
            log(f"created the first super admin ({email})")
        else:
            log(f"{users} user(s) already exist; not touching accounts")

        if public_url:
            marker = await get_row(db, MARKER)
            for key in ("deployment.frontend_url", "deployment.public_url"):
                row = await get_row(db, key)
                # Set it when unset, or when it still holds the value we set last time.
                if row is None or row.value in ("", "http://localhost:3000") or (
                    marker is not None and row.value == marker.value
                ):
                    if row is None or row.value != public_url:
                        await put(db, key, public_url)
                        changed_keys.append(key)
            await put(db, MARKER, public_url)

        row = await get_row(db, "security.trusted_proxy_ips")
        if row is None or row.value in OUR_OLD_TRUSTED:
            await put(db, "security.trusted_proxy_ips", RAILWAY_TRUSTED)
            changed_keys.append("security.trusted_proxy_ips")

        await db.commit()

    if changed_keys:
        log("set " + ", ".join(changed_keys))
        try:
            from services.redis import get_redis

            await get_redis().delete(*[f"settings:{k}" for k in changed_keys])
        except Exception as exc:  # cached values expire after 30 s anyway
            log(f"could not clear cached settings: {exc}")
    await engine.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
