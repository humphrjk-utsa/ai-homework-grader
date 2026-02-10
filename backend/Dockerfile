FROM python:3.12-slim

# System deps for psycopg2 and reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy engine and supporting files
COPY engine/ /app/engine/
COPY prompt_templates/ /app/prompt_templates/
COPY assignment_prompts/ /app/assignment_prompts/
COPY rubrics/ /app/rubrics/
COPY docker/cluster_config.docker.json /app/config/cluster_config.json

# Copy backend
COPY backend/ /app/backend/

# Symlinks so engine relative-path reads work from backend CWD
RUN ln -sf /app/prompt_templates /app/backend/prompt_templates && \
    ln -sf /app/assignment_prompts /app/backend/assignment_prompts && \
    ln -sf /app/rubrics /app/backend/rubrics && \
    ln -sf /app/config/cluster_config.json /app/backend/cluster_config.json

# Copy and set entrypoint
COPY docker/backend-entrypoint.sh /app/docker/backend-entrypoint.sh
RUN chmod +x /app/docker/backend-entrypoint.sh

# Engine imports: "from engine.X" and "from prompt_manager import X"
ENV PYTHONPATH=/app:/app/engine
ENV FLASK_APP=app:create_app
ENV FLASK_CONFIG=production

EXPOSE 5001

ENTRYPOINT ["/app/docker/backend-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "300", "--chdir", "/app/backend", "wsgi:app"]
