# ClickHouse for Agentic Resource Registry on Railway (session evidence, audit
# and telemetry tables). Official image pinned by version and digest; the
# version line matches upstream's compose file (clickhouse-server:26.6).
FROM clickhouse/clickhouse-server:26.6.8.7@sha256:2c870d77ea76e955fb1c8dad536ad40a1236b6093db0c4966e22d21d4428982b

# Upstream's config.d / users.d (memory caps, system-log TTLs, telemetry off)
# plus listen/logging settings for Railway.
COPY config.d/ /etc/clickhouse-server/config.d/
COPY users.d/ /etc/clickhouse-server/users.d/
COPY --chmod=0755 start.sh /usr/local/bin/railway-start.sh

ENV CLICKHOUSE_USER=default \
    CLICKHOUSE_DB=observal \
    CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1

EXPOSE 8123
ENTRYPOINT ["/usr/local/bin/railway-start.sh"]
