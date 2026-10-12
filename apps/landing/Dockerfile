# Build context: repository root

FROM node:20-alpine AS base
WORKDIR /app
RUN apk add --no-cache libc6-compat
ENV NEXT_TELEMETRY_DISABLED=1

FROM base AS deps
COPY packages/ui /packages/ui
COPY apps/landing/package.json apps/landing/package-lock.json ./
RUN npm ci

FROM base AS dev
ENV NODE_ENV=development
ENV NEXT_PUBLIC_APP_URL=http://localhost:3000
ENV NEXT_PUBLIC_SITE_URL=http://localhost:3002
COPY packages/ui /packages/ui
COPY --from=deps /app/node_modules ./node_modules
COPY apps/landing .
EXPOSE 3002
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3002"]

FROM base AS builder
ENV NODE_ENV=production
COPY packages/ui /packages/ui
COPY --from=deps /app/node_modules ./node_modules
COPY apps/landing .
RUN npm run build

FROM base AS runner
ENV NODE_ENV=production
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3002
ENV PORT=3002
ENV HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
