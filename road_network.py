import csv
import os
 
HERE = os.path.dirname(os.path.abspath(__file__))
 
 """This helps us find the CSV file even if we run the code from a different folder in our  Code."""
def _path(filename: str) -> str:
    return filename if os.path.isabs(filename) else os.path.join(HERE, filename)
 