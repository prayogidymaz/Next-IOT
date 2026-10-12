# Build context: repository root

FROM node:20-alpine AS base
RUN apk add --no-cache libc6-compat
ENV NEXT_TELEMETRY_DISABLED=1

FROM base AS deps
WORKDIR /repo/apps/landing
COPY packages/ui /repo/packages/ui
COPY apps/landing/package.json apps/landing/package-lock.json ./
RUN npm ci

FROM base AS dev
WORKDIR /app
ENV NODE_ENV=development
ENV NEXT_PUBLIC_APP_URL=http://localhost:3000
ENV NEXT_PUBLIC_SITE_URL=http://localhost:3002
COPY packages/ui /packages/ui
COPY --from=deps /repo/apps/landing/node_modules ./node_modules
COPY apps/landing .
EXPOSE 3002
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3002"]

FROM base AS builder
WORKDIR /repo/apps/landing
ENV NODE_ENV=production
COPY packages/ui /repo/packages/ui
COPY apps/landing/package.json apps/landing/package-lock.json ./
COPY --from=deps /repo/apps/landing/node_modules ./node_modules
COPY apps/landing .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder /repo/apps/landing/public ./public
COPY --from=builder --chown=nextjs:nodejs /repo/apps/landing/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /repo/apps/landing/.next/static ./.next/static
USER nextjs
EXPOSE 3002
ENV PORT=3002
ENV HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
