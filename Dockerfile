FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd -r -u 10001 appuser
COPY main.py keke_module.py webui.py reference_adapter.py ./
COPY DB/ ./DB/
COPY reference_os/main.py ./reference_os/main.py
COPY reference_os/DB/ ./reference_os/DB/
RUN for f in DB/*.csv; do name="${f##*/}"; if [ ! -f "reference_os/DB/$name" ]; then ln -s "../../$f" "reference_os/DB/$name"; fi; done
COPY templates/ ./templates/
COPY static/ ./static/
USER appuser
EXPOSE 8000
CMD ["sh", "-c", "exec gunicorn -w 2 -b 0.0.0.0:${PORT:-8000} --timeout 90 webui:app"]
