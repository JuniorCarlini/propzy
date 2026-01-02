FROM nginx:alpine

# Copiar configuração do Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copiar configurações de sites
COPY sites-enabled/ /etc/nginx/conf.d/

# Criar diretórios necessários
RUN mkdir -p /etc/nginx/ssl /var/www/certbot /var/log/nginx

