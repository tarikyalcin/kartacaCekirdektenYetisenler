# Build aşaması
FROM node:16-alpine as build

WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY package.json package-lock.json* ./
RUN npm install

# Uygulama kodunu kopyala
COPY . .

# Uygulamayı build et
RUN npm run build

# Üretim aşaması
FROM nginx:1.21-alpine

# Build aşamasından build dosyalarını kopyala
COPY --from=build /app/build /usr/share/nginx/html

# Nginx yapılandırması
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Port 80'i dışarıya aç
EXPOSE 80

# Nginx'i başlat
CMD ["nginx", "-g", "daemon off;"] 