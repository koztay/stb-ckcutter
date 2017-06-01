FROM nginx:1.9
MAINTAINER Nick Janetakis <nick.janetakis@gmail.com>

RUN rm /usr/share/nginx/html/*

COPY configs/nginx.conf /etc/nginx/nginx.conf
COPY configs/default.conf /etc/nginx/conf.d/default.conf

COPY certs/istebu_com_bundle.crt /etc/ssl/certs/istebu_com_bundle.crt
COPY certs/istebu.key /etc/ssl/private/istebu.key
COPY certs/dhparam.pem /etc/ssl/private/dhparam.pem

COPY docker-entrypoint /
RUN chmod +x /docker-entrypoint
ENTRYPOINT ["/docker-entrypoint"]

CMD ["nginx", "-g", "daemon off;"]
