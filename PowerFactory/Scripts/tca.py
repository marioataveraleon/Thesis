import pf_utils
import importlib
import pandas as pd
import numpy as np

def main():
    app = pf_utils.connect_to_powerfactory()

    # Relevante netzobjekte lesen

    terminals = app.GetCalcRelevantObjects("*.ElmTerm")
    lines = app.GetCalcRelevantObjects("*.ElmLne")
    trafos = app.GetCalcRelevantObjects("*.ElmTr2")
    app.PrintPlain(f"Len Terminals: {len(terminals)}")
    app.PrintPlain(f"Len lines: {len(lines)}")
    app.PrintPlain(f"Len trafos: {len(trafos)}")

    ## Execute Loadflow

    ldf = app.GetFromStudyCase('ComLdf')
    ldf.Execute()


    ## Get the voltage and current to calculate Smax
    rows_lines = []
    for line in lines:
        name = line.loc_name
        ltype = line.typ_id
        uline = ltype.uline #kV
        iline = ltype.sline # kA
        smax = np.sqrt(3) * uline * iline #MVA
        loading = line.GetAttribute('c:loading')
        p_used = (loading/100) * smax 
        margin = smax - p_used
        rows_lines.append({"name": name,"uline":uline,"iline":iline,
                           "smax":smax,"loading":loading,"p_used":p_used,
                           "margin": margin})
        #app.PrintPlain(f"name: {name} & smax: {smax} & loading: {loading} & pused: {p_used} & margin: {margin}")
    
    rows_trafos = []
    for trafo in trafos:
        name = trafo.loc_name
        ttype = trafo.typ_id
        smax = ttype.strn
        loading = trafo.GetAttribute('c:loading')
        p_used = (loading/100) * smax
        margin = smax - p_used
        rows_trafos.append({"name":name,"smax": smax,"loading":loading,
                            "p_used":p_used,"margin": margin})
        #app.PrintPlain(f"name: {name} smax: {smax} & loading {loading} & pused:{p_used} & margin: {margin}")

    ## Check if there is a SetSelect Element that contains the buses ('Set - Busbars') 

    study = app.GetActiveStudyCase()
    sets = study.GetContents('*.SetSelect')
    bus_set = None
    for s in sets:
        if s.loc_name == "Set - Busbars":
            bus_set = s
            app.PrintPlain(f"Set Select Busbars founded!! :) : {bus_set}")
            break
    if bus_set is None:
        app.PrintPlain("No Set Select Busbars founded, creating object...")
        bus_set = study.CreateObject('SetSelect','Set - Busbars')
        bus_set.iused = 31 #Sensitivity Analysis / Distribution Factors
        bus_set.iusedSub = 1 #Busbars
        bus_set.AddRef(terminals) # Add the terminals to the setselect object


    ## Running the sensitivity analysis
    use_contingencies = 1 # 1:consider contingencies, 0 without contingencies
    ptdf = app.GetFromStudyCase('*.ComVstab')
    ptdf.SetAttribute('isContSens',use_contingencies)
    ptdf.SetAttribute('calcPtdf',1)
    ptdf.SetAttribute('calcLodf',1)
    ptdf.p_bus = bus_set
    if use_contingencies == 1:
        app.PrintPlain("Contingencies are considered")
        contingency = None
        contingencies = study.GetContents('*.ComSimoutage')
        for c in contingencies:
            if c.loc_name == "Contingencies for HCA":
                contingency = c
                app.PrintPlain(f"Contingengy for HCA Analysis founded: {c}")
                break
        if contingency is None:
            app.PrintPlain("No Contingency object found, creating object...")
            cntg_def = study.CreateObject('ComNmink','CntDefHCA')
            cntg_def.iopt_cmd = 0 # Create fault cases
            cntg_def.iopt_n1 = 1 # n-1 
            cntg_def.optSel = 0 # Whole system
            cntg_def.iopt_lne = 1 #Lines
            cntg_def.iopt_trf = 1 # Trafos
            cntg_def.iopt_sym = 0 # Generators
            cntg_def.iopt_scap = 0  # Capacitors
            cntg_def.iopt_sreac = 0 # Reactances
            cntg_def.cntNameDef = 1 # Name definition
            contingency = study.CreateObject('ComSimoutage','Contingencies for HCA')
            contingency.iopt_Linear = 1 #DC Calculation



    #ptdf.Execute()

  

if __name__ == "__main__":
    main()