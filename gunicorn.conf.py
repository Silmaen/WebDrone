"""Gunicorn configuration."""
# Only check X-Forwarded-Proto for scheme detection.
# Prevents "Contradictory scheme headers" when a reverse proxy
# sets X-Forwarded-Proto but not X-Forwarded-Protocol / X-Forwarded-SSL.
secure_scheme_headers = {"X-FORWARDED-PROTO": "https"}
forwarded_allow_ips = "*"
