"""Container health probe.

Calls Django's /healthz/ endpoint over HTTP. The X-Forwarded-Proto header keeps
the probe working when SECURE_SSL_REDIRECT is enabled (the proxy terminates TLS
in front of the container). The Host header uses the first configured allowed
host so ALLOWED_HOSTS does not need to include 127.0.0.1.
"""

import http.client
import os
import sys


def main() -> int:
    allowed_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost")
    host_header = allowed_hosts.split(",")[0].strip() or "localhost"
    port = int(os.environ.get("PORT", "8000"))

    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request(
            "GET",
            "/healthz/",
            headers={
                "Host": host_header,
                "X-Forwarded-Proto": "https",
            },
        )
        response = connection.getresponse()
        response.read()
        return 0 if response.status == 200 else 1
    except Exception as exc:  # noqa: BLE001 - health checks should never raise
        print(f"Health check failed: {exc}", file=sys.stderr)
        return 1
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
