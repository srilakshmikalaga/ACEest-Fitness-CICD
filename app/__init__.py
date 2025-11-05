import os
import sys

# Add project root to PYTHONPATH automatically when 'app' is imported
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
