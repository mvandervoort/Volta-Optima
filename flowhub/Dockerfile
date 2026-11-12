FROM oven/bun:1 AS build
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile
COPY . .
RUN bun run build

FROM oven/bun:1
WORKDIR /app
ENV NODE_ENV=production \
    FLOWHUB_PORT=8080 \
    FLOWHUB_CONFIG=/etc/flowhub/config.json \
    FLOWHUB_DATA_DIR=/data

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile --production

COPY --from=build /app/src ./src
COPY --from=build /app/dist ./dist
COPY --from=build /app/scripts ./scripts

RUN mkdir -p /data && chown -R bun:bun /data
USER bun

EXPOSE 8080
VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD bun -e "fetch('http://127.0.0.1:8080/api/v1/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["bun", "src/server/index.ts"]