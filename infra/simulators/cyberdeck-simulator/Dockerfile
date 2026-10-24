FROM python:3.12-slim
WORKDIR /app
COPY apps/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY apps/api /app
ENV PYTHONPATH=/app
CMD ["python", "-m", "app.mesh_simulators.cli", "cyberdeck"]
