from __future__ import annotations

from datetime import UTC, datetime
import json

from app.core.config import PROJECT_ROOT


def send_password_reset_email(*, recipient: str, temporary_password: str) -> dict[str, str]:
    outbox_path = PROJECT_ROOT / "database" / "mail_outbox.jsonl"
    outbox_path.parent.mkdir(parents=True, exist_ok=True)
    message = {
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "to": recipient,
        "subject": "FIDUCIA - Recuperacion de contrasena",
        "body": (
            "Solicitaste recuperar tu acceso a FIDUCIA. "
            f"Tu contrasena temporal es: {temporary_password}. "
            "Al ingresar, el sistema solicitara crear una nueva contrasena."
        ),
    }
    with outbox_path.open("a", encoding="utf-8") as outbox:
        outbox.write(json.dumps(message, ensure_ascii=False) + "\n")
    return {"delivery": "simulated_email", "outbox": str(outbox_path)}
