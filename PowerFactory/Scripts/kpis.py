import pandas as pd
import numpy as np
from typing import Optional,Tuple,Dict


# HELPERS
def load_pf_csv(path: str) -> pd.DataFrame:
    """
    Load a CSV exported by PowerFactory
    """
    df = pd.read_csv(path)
    return df


def get_series(df: pd.DataFrame, colmap:Dict[str,str], key:str)-> pd.Series:
    """
    Receives a Dataframe in order to search for the column
    Colmap is a dictionary, where the mapping of the desired variable with the 
        respective column will happen i.e. in Dict {f:Electrical frequency}
        I search for the key "f"
    key: name of the variable i want to search for
    """
    

def window_mask(t:np.ndarray,t0:float,t1:float) -> np.ndarray:
    return(t >= t0) & (t<=t1)

def finite_diff_derivative(t: np.ndarray, y:np.ndarray) ->np.ndarray:
    """
    This function calculates the derivative dy/dt
    Return an array of the same length of y
    """
    dydt = np.gradient(y,t)
    return dydt

# Load step:
# Obligatorio:fnadir, RoCoF, Settling time de frecuencia ; opcionales: frequency overshoot (fmax)
#Delta P aplicado (verificacion del step), Settling de Potencia, EQSG speed min/mac

# 3 PHSC: 
# Obligatorio: