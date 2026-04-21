# syntax=docker/dockerfile:1.7

FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Baked into the Vite build so the SPA knows the absolute backend URL on
# Railway (where frontend and backend are separate services, not same-origin).
# Empty at local compose build = falls back to relative /api via nginx proxy.
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

FROM nginx:alpine

# Template the config so ${PORT} gets substituted at container start.
# Railway injects PORT dynamically; default to 80 for local runs.
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html

ENV PORT=80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
