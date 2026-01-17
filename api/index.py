
import os
import sys

# Add the 'agents' directory to sys.path so that internal imports (like 'from config import...') work
sys.path.append(os.path.join(os.path.dirname(__file__), '../agents'))

from app import app
