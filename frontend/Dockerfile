FROM node:20-alpine AS build

# Inject API URL at build time so VITE_API_URL is baked into the bundle
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Use unprivileged nginx image (runs as non-root on port 8080)
FROM nginxinc/nginx-unprivileged:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
