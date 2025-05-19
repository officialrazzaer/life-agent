import sys
import os
# Ensure the project root is in sys.path so 'src' is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.db.vector_store import ChromaDBManager

USAGE = """
Usage:
  python3 scripts/chroma_clear.py --all
  python3 scripts/chroma_clear.py --date YYYY-MM-DD
"""

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    chroma = ChromaDBManager(collection_name="my_life_logs")

    if sys.argv[1] == "--all":
        chroma.delete_all_data()
    elif sys.argv[1] == "--date" and len(sys.argv) == 3:
        date_str = sys.argv[2]
        chroma.delete_data_by_date(date_str)
    else:
        print(USAGE)
        sys.exit(1)

if __name__ == "__main__":
    main() 