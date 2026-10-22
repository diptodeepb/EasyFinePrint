"""Vercel Serverless Function entrypoint for standalone backend deployment."""
import os
import sys

# Ensure backend root directory is on sys.path so 'app.*' imports resolve cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app  # noqa: F401, E402
