FROM node:24.16.0-alpine AS build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
COPY design/ /app/design/
RUN npm run build

FROM nginx:1.29.3-alpine
RUN sed -i 's|^pid[[:space:]]*[^;]*;|pid /tmp/nginx.pid;|' /etc/nginx/nginx.conf \
    && sed -i '/^http {/a\    client_body_temp_path /tmp/client_temp;' /etc/nginx/nginx.conf \
    && sed -i '/^http {/a\    proxy_temp_path /tmp/proxy_temp;' /etc/nginx/nginx.conf \
    && sed -i '/^http {/a\    fastcgi_temp_path /tmp/fastcgi_temp;' /etc/nginx/nginx.conf \
    && sed -i '/^http {/a\    uwsgi_temp_path /tmp/uwsgi_temp;' /etc/nginx/nginx.conf \
    && sed -i '/^http {/a\    scgi_temp_path /tmp/scgi_temp;' /etc/nginx/nginx.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 5173
CMD ["nginx","-g","daemon off;"]
