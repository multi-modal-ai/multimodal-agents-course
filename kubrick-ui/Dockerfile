FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY bun.lockb ./

RUN npm i

COPY . .

RUN npm run build

# ------------------------------------------------------------

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
