# Build context: repository root (see docker-compose.yml `admin.build.context`).

FROM node:20-alpine AS base
RUN apk add --no-cache libc6-compat
ENV NEXT_TELEMETRY_DISABLED=1

FROM base AS deps
WORKDIR /repo/apps/admin
COPY packages/ui /repo/packages/ui
COPY apps/admin/package.json apps/admin/package-lock.json ./
RUN npm ci

FROM base AS dev
WORKDIR /app
ENV NODE_ENV=development
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV API_PROXY_TARGET=http://api:8000
COPY packages/ui /packages/ui
COPY --from=deps /repo/apps/admin/node_modules ./node_modules
COPY apps/admin .
EXPOSE 3001
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3001"]

FROM base AS builder
WORKDIR /repo/apps/admin
ENV NODE_ENV=production
COPY packages/ui /repo/packages/ui
COPY apps/admin/package.json apps/admin/package-lock.json ./
COPY --from=deps /repo/apps/admin/node_modules ./node_modules
COPY apps/admin .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV API_PROXY_TARGET=http://api:8000
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder /repo/apps/admin/public ./public
COPY --from=builder --chown=nextjs:nodejs /repo/apps/admin/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /repo/apps/admin/.next/static ./.next/static
USER nextjs
EXPOSE 3001
ENV PORT=3001
ENV HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
