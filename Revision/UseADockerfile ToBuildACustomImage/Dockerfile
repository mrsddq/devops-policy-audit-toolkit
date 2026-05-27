FROM nginx:1.27.5-alpine
COPY custom.html /usr/share/nginx/html/index.html
USER nginx
CMD ["nginx", "-g", "daemon off;"]
