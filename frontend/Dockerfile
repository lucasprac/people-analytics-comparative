FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci && npm install -g http-server
COPY . .
RUN [ -f angular.json ] && npm run build || echo "No Angular project, skipping build"

FROM nginx:alpine
COPY --from=build /app/dist/frontend /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
