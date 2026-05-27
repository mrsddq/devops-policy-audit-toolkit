FROM python:3.11.9-slim-bookworm

WORKDIR /app

COPY . .

CMD ["python", "-m", "devops_toolkit.cli", "--strict"]
