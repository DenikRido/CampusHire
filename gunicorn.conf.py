import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = int(os.environ.get("GUNICORN_WORKERS", str(max(2, multiprocessing.cpu_count()))))
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
timeout = 60
accesslog = "-"
errorlog = "-"
capture_output = True
