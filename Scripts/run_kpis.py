import sys
from pathlib import Path

# ruta al repo
REPO_ROOT = Path(__file__).resolve().parents[1]   # ajusta si tu árbol es distinto
PF_SCRIPTS = REPO_ROOT / "PowerFactory" / "Scripts"

sys.path.insert(0, str(PF_SCRIPTS))

import kpis

print("kpis imported correctly")

results_path = r"C:\Users\UI450907\Desktop\TE RWEST\Tesis\Results\GFL_IEC\E2_3PhSC\E2_3PhSC.csv"

colmap = {
    "t": "All Calculations",
    "f": "PCR",
    "V": "PCR.1",
    "w_eqsg":"EQ_SG",
    "P": "WT Type 4B",
    "Q": "WT Type 4B.2",
    "Ipos": "WT Type 4B.2", 
}



df = kpis.load_pf_csv(results_path)

f=kpis.get_series(df,colmap,"f")
print(f)
