FROM nginx:1.27.5-alpine
COPY custom.html /usr/share/nginx/html/index.html
RUN sed -i 's/listen       80;/listen       8080;/' /etc/nginx/conf.d/default.conf \
    && sed -i 's/^user  nginx;/# user directive omitted for non-root container;/' /etc/nginx/nginx.conf \
    && sed -i 's#pid        /run/nginx.pid;#pid        /tmp/nginx.pid;#' /etc/nginx/nginx.conf \
    && chown -R nginx:nginx /var/cache/nginx /var/log/nginx /usr/share/nginx/html
USER nginx
CMD ["nginx", "-g", "daemon off;"]
