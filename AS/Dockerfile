FROM python:3.10-slim
WORKDIR /app
COPY server.py .
EXPOSE 53533/udp
CMD ["python", "-u", "server.py"]