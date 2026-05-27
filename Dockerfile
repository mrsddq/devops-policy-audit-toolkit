FROM python:3.12.7-slim-bookworm

WORKDIR /app
COPY pyproject.toml README.md ./
COPY devops_toolkit ./devops_toolkit
RUN pip install --no-cache-dir .

RUN useradd --create-home --shell /bin/bash appuser
USER appuser
ENTRYPOINT ["devops-audit"]
CMD ["/repo"]
