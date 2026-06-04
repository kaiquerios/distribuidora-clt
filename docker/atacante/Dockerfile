FROM alpine:3.19

RUN apk add --no-cache openssh python3 py3-pip

RUN pip3 install cryptography --break-system-packages

RUN ssh-keygen -A
RUN echo "root:clt2026" | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

RUN mkdir -p /logs

CMD ["/usr/sbin/sshd", "-D"]