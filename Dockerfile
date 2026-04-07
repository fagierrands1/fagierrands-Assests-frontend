FROM nginx:alpine

COPY static /usr/share/nginx/html/static
COPY staticfiles /usr/share/nginx/html/staticfiles
COPY templates /usr/share/nginx/html/templates

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 10000

CMD ["nginx", "-g", "daemon off;"]
