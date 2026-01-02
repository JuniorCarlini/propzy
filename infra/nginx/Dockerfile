FROM nginx:alpine

# Instalar OpenSSL para gerar certificados temporários
RUN apk add --no-cache openssl

# Copiar script de entrypoint
COPY entrypoint.sh /docker-entrypoint.d/99-ssl-setup.sh
RUN chmod +x /docker-entrypoint.d/99-ssl-setup.sh

# Copiar configuração do Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copiar configurações de sites
COPY sites-enabled/ /etc/nginx/conf.d/

# Criar diretórios necessários
RUN mkdir -p /etc/nginx/ssl /var/www/certbot /var/log/nginx

