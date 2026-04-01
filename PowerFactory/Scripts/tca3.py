import pf_utils
import importlib
import pandas as pd
import numpy as np
import os
import tca
import re

def main():
    base_path = r"C:\Users\UI450907\Desktop\TE RWEST\Tesis\Phase3Results"
    app = pf_utils.connect_to_powerfactory()
    # Relevante netzobjekte lesen
    terminals,lines,trafos = tca.get_relevant_objects(app)

    for line in lines:
        line.outserv = 0
    for trafo in trafos:
        trafo.outserv = 0



if __name__ == "__main__":
    main()