# Agentic Resource Registry web UI for Railway: the official image (nginx serving
# the built SPA), pinned by version and digest, with an nginx config that listens
# on PORT and proxies /api to the api service over Railway's private network.
# Bump the pin here (and in api/Dockerfile) to ship an update.
FROM ghcr.io/agenticresourceregistry/observal-web:1.17.1@sha256:ee0de5fc0ea8689f4a5a22e3ac6381041da9aa3c47dabdede2f347772220998a

COPY default.conf.template /etc/nginx/templates/default.conf.template

# PORT: where Railway's public domain points. API_HOST / API_PORT: the api
# service on the private network (the template sets them by reference).
# The local-resolvers step puts the container's DNS server (IPv6 on Railway)
# into NGINX_LOCAL_RESOLVERS, so *.railway.internal resolves at request time.
ENV PORT=8080 \
    API_HOST=api.railway.internal \
    API_PORT=8000 \
    NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1 \
    NGINX_ENVSUBST_FILTER="^(PORT|API_HOST|API_PORT|NGINX_LOCAL_RESOLVERS)\$"

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
