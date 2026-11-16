# Site estático (HTML único) servido pelo nginx — deploy no Coolify do LC PETRO (porta 80)
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
