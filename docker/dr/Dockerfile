FROM alpine:3.19
RUN apk add --no-cache python3 sqlite
RUN mkdir -p /app/banco /app/logs
COPY init_dr.py /app/init_dr.py
WORKDIR /app
CMD ["python3", "init_dr.py"]