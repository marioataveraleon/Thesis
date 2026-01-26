import pandas as pd
import numpy as np
from typing import Optional,Tuple,Dict


# HELPERS
def load_pf_csv(path: str) -> pd.DataFrame:
    """
    Load a CSV exported by PowerFactory
    """
    df = pd.read_csv(path)
    print("df imported properly")
    return df


def get_series(df: pd.DataFrame, colmap:Dict[str,str], key:str)-> pd.Series:
    """
    Receives a Dataframe in order to search for the column
    Colmap is a dictionary, where the mapping of the desired variable with the 
        respective column will happen i.e. in Dict {f:Electrical frequency}
        I search for the key "f"
    key: name of the variable i want to search for
    """
    if key not in colmap:
        raise KeyError(f"Missing key: {key} in colmap")
    col = colmap[key]
    if col not in df.columns:
        print(f"Column {col} not found in the CSV")
        print(f"Available columns: {df.columns}")
    return df[col]
    

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
# Obligatorio:fnadir, RoCoF, Settling time de frecuencia ; 
# opcionales: frequency overshoot (fmax)
#Delta P aplicado (verificacion del step), Settling de Potencia, EQSG speed min/max
def kpi_f_nadir(df, colmap, t0: float, t1: float ) -> float:
    t = get_series(df, colmap, "t").to_numpy()
    f = get_series(df, colmap, "f").to_numpy()

    m = window_mask(t, t0, t1)
    return float(f[m].min())
 
def kpi_rocof_max(df,colmap,t0:float,t1:float) -> float:
    t=get_series(df,colmap,"t").to_numpy()
    f=get_series(df,colmap,"f").to_numpy()
    m = window_mask(t,t0,t1)
    dfdt = finite_diff_derivative(m[t],f[m]) #df/dt
    idx = np.argmax(np.abs(dfdt))
    return float(dfdt[idx])

def kpi_settling_time_f(df,colmap,t_event:float,
                        f_ref:float =50.0, band_hz:float = 0.5,
                        hold_s:float = 0.5,t_end:float = 20):
    t = get_series(df,colmap,"t").to_numpy()
    f = get_series(df, colmap,"f").to_numpy()
    m = window_mask(t,t_event,t_end)

    tt, ff = t[m],f[m]
    
    inside = np.abs(ff - f_ref) <= band_hz

    for i in range(len(tt)):
        if not inside[i]:
            continue
        t_i = tt[i]
        m_hold = (tt >= t_i) & (tt <= t_i + hold_s)
        if m_hold.any() and inside[m_hold].all():
            return float(t_i - t_event)

    return None  # no asienta

def kpi_f_overshoot(df, colmap, t_event: float, T: float = 10.0) -> float:
    t = get_series(df, colmap, "t").to_numpy()
    f = get_series(df, colmap, "f").to_numpy()
    m = window_mask(t, t_event, t_event + T)
    return float(f[m].max())


def kpi_delta_P(df, colmap, t_event: float,
                pre=( -1.0, -0.1), post=( 1.0, 3.0)) -> float:
    t = get_series(df, colmap, "t").to_numpy()
    P = get_series(df, colmap, "P").to_numpy()

    mpre  = window_mask(t, t_event + pre[0],  t_event + pre[1])
    mpost = window_mask(t, t_event + post[0], t_event + post[1])

    Ppre  = P[mpre].mean()
    Ppost = P[mpost].mean()
    return float(Ppost - Ppre)

def kpi_settling_time_P(df, colmap, t_event: float,
                        band_frac: float = 0.01, hold_s: float = 0.5,
                        post=(1.0, 3.0), t_end: float = 20.0):
    t = get_series(df, colmap, "t").to_numpy()
    P = get_series(df, colmap, "P").to_numpy()

    # steady-state target from post-window average
    mpost = window_mask(t, t_event + post[0], t_event + post[1])
    P_ref = float(P[mpost].mean())
    band = band_frac * abs(P_ref)

    m = window_mask(t, t_event, t_end)
    tt, PP = t[m], P[m]
    inside = np.abs(PP - P_ref) <= band

    for i in range(len(tt)):
        if not inside[i]:
            continue
        t_i = tt[i]
        m_hold = (tt >= t_i) & (tt <= t_i + hold_s)
        if m_hold.any() and inside[m_hold].all():
            return float(t_i - t_event)
    return None

def kpi_eqsg_speed_minmax(df, colmap, t0: float, t1: float):
    t = get_series(df, colmap, "t").to_numpy()
    w = get_series(df, colmap, "w_eqsg").to_numpy()
    m = window_mask(t, t0, t1)
    return float(w[m].min()), float(w[m].max())

# 3 PHSC: 
# Obligatorio: Voltage dip (Vmin) en pcr, Voltage recovery time t_0.9 or t_0.95.,
#Max positive sequence current I+_max, Max reactive power injection, Q_max
#Opcionales: Active power curtailment P_min, Active Power recovery time t_rec,P-
#Freq nadir post fault, con ventana post clearing, RoCoF, con ventana post clearing


def kpi_Vmin_fault(df, colmap, t_fault: float, t_clear: float) -> float:
    t = get_series(df, colmap, "t").to_numpy()
    V = get_series(df, colmap, "V").to_numpy()
    m = window_mask(t, t_fault, t_clear)
    return float(V[m].min())

def kpi_V_recovery_time(df, colmap, t_clear: float, Vthr: float = 0.95,
                        exclude_s: float = 0.05, hold_s: float = 0.2,
                        t_end: float = 20.0):
    t = get_series(df, colmap, "t").to_numpy()
    V = get_series(df, colmap, "V").to_numpy()

    m = window_mask(t, t_clear + exclude_s, t_end)
    tt, VV = t[m], V[m]
    ok = VV >= Vthr

    for i in range(len(tt)):
        if not ok[i]:
            continue
        t_i = tt[i]
        m_hold = (tt >= t_i) & (tt <= t_i + hold_s)
        if m_hold.any() and ok[m_hold].all():
            return float(t_i - t_clear)
    return None

def kpi_Ipos_max(df, colmap, t0: float, t1: float) -> float:
    t = get_series(df, colmap, "t").to_numpy()
    I = get_series(df, colmap, "Ipos").to_numpy()
    m = window_mask(t, t0, t1)
    return float(I[m].max())

def kpi_Pmin_fault(df, colmap, t0: float, t1: float) -> float:
    t = get_series(df, colmap, "t").to_numpy()
    P = get_series(df, colmap, "P").to_numpy()
    m = window_mask(t, t0, t1)
    return float(P[m].min())
def kpi_P_recovery_time(df, colmap, t_clear: float,
                        alpha: float = 0.95,
                        pre=(-1.0, -0.1),
                        exclude_s: float = 0.05,
                        hold_s: float = 0.2,
                        t_end: float = 20.0):
    t = get_series(df, colmap, "t").to_numpy()
    P = get_series(df, colmap, "P").to_numpy()

    # pre-fault reference
    mpre = window_mask(t, t_clear + pre[0], t_clear + pre[1])
    Ppre = float(P[mpre].mean())
    target = alpha * Ppre

    m = window_mask(t, t_clear + exclude_s, t_end)
    tt, PP = t[m], P[m]
    ok = PP >= target

    for i in range(len(tt)):
        if not ok[i]:
            continue
        t_i = tt[i]
        m_hold = (tt >= t_i) & (tt <= t_i + hold_s)
        if m_hold.any() and ok[m_hold].all():
            return float(t_i - t_clear)
    return None





