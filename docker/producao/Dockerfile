FROM alpine:3.19
RUN apk add --no-cache python3 sqlite
RUN mkdir -p /app/banco /app/backup /app/logs
COPY init_banco.py /app/init_banco.py
WORKDIR /app
CMD ["python3", "init_banco.py"]