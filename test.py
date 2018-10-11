from pathlib import Path
import pandas
import os

curr_dir, curr_file = os.path.split(os.path.abspath(__file__))
dir = Path(curr_dir)
p = dir / "json" / "week{}.json".format(0)
open(p, "w")
