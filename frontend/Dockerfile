# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY --from=builder /app/.next ./.next
COPY public ./public
COPY next.config.ts ./

EXPOSE 3000

CMD ["npm", "start"]
