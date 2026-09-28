import csv
import os
 
HERE = os.path.dirname(os.path.abspath(__file__))
 
 """This helps us find the CSV file even if we run the code from a different folder in our  Code."""
def _path(filename: str) -> str:
    return filename if os.path.isabs(filename) else os.path.join(HERE, filename)

 """This function reads every road from the CSV and returns the graph."""
def load_road_network(filename: str = "Q2_road_network.csv", verbose: bool = False) -> dict:
    roads = {}          # key = the two junctions in sorted order, value = minutes
    duplicates = []     # any road we see a second time goes here as a duplicate
 
    # We read the file row by row and store each road only once.
    with open(_path(filename), newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            a, b = row["from"].strip(), row["to"].strip()
            minutes = int(row["minutes"])