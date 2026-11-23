# Agentic Resource Registry API + background worker for Railway.
# The official image, pinned by version and digest, plus a small start script.
# Bump the pin here (and in web/Dockerfile) to ship an update.
FROM ghcr.io/agenticresourceregistry/observal-api:1.17.1@sha256:feddb15b7c8c52b157e5aa72e708395045fa4f3af774ae352e8f608661de2253

# The start script runs as root only to make the Railway volume (/data, mounted
# root-owned) writable, then runs every app process as the image's appuser (1001).
USER root
COPY --chmod=0755 start.sh /railway/start.sh
COPY --chmod=0644 bootstrap.py serve.py /railway/

ENV PORT=8000 \
    JWT_KEY_DIR=/data/keys \
    MIGRATION_ARTIFACT_ROOT=/data/migration_artifacts \
    SKIP_DDL_ON_STARTUP=true

EXPOSE 8000
CMD ["/railway/start.sh"]
