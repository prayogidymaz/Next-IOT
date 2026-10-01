# Build context: repository root (see docker-compose.yml `web.build.context`).

FROM node:20-alpine AS base
WORKDIR /app
RUN apk add --no-cache libc6-compat
ENV NEXT_TELEMETRY_DISABLED=1

FROM base AS deps
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci

# --- Development (hot reload) — default for root docker-compose.yml ---
FROM base AS dev
ENV NODE_ENV=development
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV API_PROXY_TARGET=http://api:8000
COPY --from=deps /app/node_modules ./node_modules
COPY apps/web .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]

# --- Production (standalone) ---
FROM base AS builder
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY apps/web .
RUN npm run build

FROM base AS runner
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV API_PROXY_TARGET=http://api:8000
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
