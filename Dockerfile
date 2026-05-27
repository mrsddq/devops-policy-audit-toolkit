FROM python:3.11.9-slim-bookworm

WORKDIR /app

COPY . .

CMD ["python", "scripts/devops_audit.py", "--strict"]
