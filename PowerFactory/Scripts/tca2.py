import pf_utils
import importlib
import pandas as pd
import numpy as np
import os
import tca
import re
import time

def get_smax_dicts(lines, trafos):

    # --- Lines ---
    df_smax_lines = []
    for line in lines:
        name = line.loc_name
        ltype = line.typ_id
        smax = np.sqrt(3) * ltype.uline * ltype.sline

        df_smax_lines.append({
            "name": name,
            "smax": smax
        })

    df_smax_lines = pd.DataFrame(df_smax_lines)

    # --- Trafos ---
    df_smax_trafos = []
    for trafo in trafos:
        name = trafo.loc_name
        ttype = trafo.typ_id
        smax = ttype.strn

        df_smax_trafos.append({
            "name": name,
            "smax": smax
        })

    df_smax_trafos = pd.DataFrame(df_smax_trafos)

    # --- Dicts (más rápido para loops grandes) ---
    smax_lines_dict = dict(zip(df_smax_lines["name"], df_smax_lines["smax"]))
    smax_trafos_dict = dict(zip(df_smax_trafos["name"], df_smax_trafos["smax"]))

    return smax_lines_dict, smax_trafos_dict

def get_case_limits(app,lines, trafos, smax_lines_dict, smax_trafos_dict):

    # --- Líneas ---
    rows_lines = []

    for line in lines:
        if line.outserv == 1:
            app.PrintPlain(f"Skipping out of service line: {line.loc_name}, has no loading")
            continue
        name = line.loc_name
        loading = line.GetAttribute('c:loading')
        p_terminali = line.GetAttribute('m:P:bus1')
        smax = smax_lines_dict.get(name, np.nan)

        if loading is None:
            loading = np.nan

        #actual = (loading / 100) * smax if pd.notna(loading) else np.nan
        #margin = smax - actual if pd.notna(actual) else np.nan
        margin = smax - p_terminali

        rows_lines.append({
            "name": name,
            "smax": smax,
            "loading": loading,
            "actual": p_terminali,
            "margin": margin
        })

    df_lines = pd.DataFrame(rows_lines)

    # --- Trafos ---
    rows_trafos = []

    for trafo in trafos:
        if trafo.outserv == 1:
            app.PrintPlain(f"Skipping trafo: {trafo}, has no loading")
            continue
        name = trafo.loc_name
        phv = trafo.GetAttribute('m:P:bushv')
        loading = trafo.GetAttribute('c:loading')
        smax = smax_trafos_dict.get(name, np.nan)

        if loading is None:
            loading = np.nan

        # actual = (loading / 100) * smax if pd.notna(loading) else np.nan
        # margin = smax - actual if pd.notna(actual) else np.nan
        margin = smax - phv

        rows_trafos.append({
            "name": name,
            "smax": smax,
            "loading": loading,
            "actual": phv,
            "margin": margin
        })

    df_trafos = pd.DataFrame(rows_trafos)

    return df_lines, df_trafos

def run_contingency_cases(app,lines,trafos,smax_lines_dict,smax_trafos_dict,loadings):

    for line_out in lines:
        case_name = re.sub(r"_+", "_", f"{line_out.loc_name}_Cnt".replace("-", "_").replace(" ", "_"))
        app.PrintPlain(f"Line out: {line_out.loc_name}")

        line_out.outserv = 1
        rc = tca.execute_ldf(app)

        if rc == 0:
            app.PrintPlain(f"Load flow OK: {rc}, getting limits")
            df_lines, df_trafos = get_case_limits(app, lines, trafos, smax_lines_dict, smax_trafos_dict)
            df = pd.concat([df_lines, df_trafos], ignore_index=True)
            loadings[case_name] = df
        else:
            app.PrintPlain(f"LoadFlow did not converge for {case_name}")

        line_out.outserv = 0
        tca.execute_ldf(app)
            

    for trafo_out in trafos:
        name = trafo_out.loc_name
        case_name = re.sub(r"_+", "_", f"{name}_Cnt".replace("-", "_").replace(" ", "_"))
        trafo_out.outserv = 1
        rc = tca.execute_ldf(app)
        if rc == 0:
            df_lines, df_trafos = get_case_limits(app,
                lines, trafos, smax_lines_dict, smax_trafos_dict
            )
            df = pd.concat([df_lines, df_trafos], ignore_index=True)
            loadings[case_name] = df
        else:
            app.PrintPlain(f"Loadflow did not converge for {case_name}")
        trafo_out.outserv = 0
        tca.execute_ldf(app)
    return loadings

def put_all_lines_trafos_inservice(app,lines,trafos):
    for line in lines:
        line.outserv = 0 #In service
    for trafo in trafos:
        trafo.outserv = 0 # In service
    app.PrintPlain("All Lines & Trafos in Service")
    tca.execute_ldf(app)




def main():
    start = time.time()
    base_path = r"C:\Users\UI450907\Desktop\TE RWEST\Tesis\Phase3Results"
    app = pf_utils.connect_to_powerfactory()
    loadings = {}

    # Relevante netzobjekte lesen
    terminals,lines,trafos = tca.get_relevant_objects(app)
    ## Execute Loadflow
    #Get Static Data
    smax_lines_dict,smax_trafos_dict = get_smax_dicts(lines,trafos)
    # Run load flow and get loading for base case
    ldf = app.GetFromStudyCase('ComLdf')
    rc = ldf.Execute()
    if rc == 0:
        app.PrintPlain(f"Load flow for Base Case calculated: {rc}")
        df_lines,df_trafos = get_case_limits(app,lines,trafos,smax_lines_dict,smax_trafos_dict)
        df = pd.concat([df_lines,df_trafos],ignore_index= True)
        loadings["Base Case"] = df
    else:
        app.PrintPlain(f"Loadflow for the basecase did not converged, rc: {rc}")

    put_all_lines_trafos_inservice(app,lines,trafos)
    loadings = run_contingency_cases(app,lines,trafos,smax_lines_dict,smax_trafos_dict,loadings)
    df_all = []

    for case, df in loadings.items():
        df_copy = df.copy()
        df_copy["case"] = case
        df_all.append(df_copy)

    df_all = pd.concat(df_all, ignore_index=True)
    df_all.to_csv(rf"{base_path}\loadings_all.csv", index=False)
    app.PrintPlain(f"Results exported:{base_path}\loadings_all.csv ")
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
            app.PrintPlain("No Contingency object found, creating definition object...")
            cntg_def = study.CreateObject('ComNmink','CntDefHCA')
            cntg_def.iopt_cmd = 1 # Generate contingency for analysis
            cntg_def.iopt_n1 = 1 # n-1 
            cntg_def.optSel = 0 # Whole system
            cntg_def.iopt_lne = 1 #Lines
            cntg_def.iopt_trf = 1 # Trafos
            cntg_def.iopt_sym = 0 # Generators
            cntg_def.iopt_scap = 0  # Capacitors
            cntg_def.iopt_sreac = 0 # Reactances
            cntg_def.cntNameDef = 1 # Name definition
            #Creating Contingency Analysis
            app.PrintPlain(f"Definition object Created: {cntg_def}. Creating contingencies...")
            contingency = study.CreateObject('ComSimoutage','Contingencies for HCA')
            rc = cntg_def.GenerateContingenciesForAnalysis()
            if rc == 0:
                outs  = contingency.GetContents('*.ComOutage')
                app.PrintPlain(f"Succes: {len(outs)} contingencies created")
            else:
                app.PrintPlain("Error generating contingencies")
        if contingency is not None:
            ptdf.pComSimoutage = contingency
    ptdf.Execute()

    ## Export Results
    res_list = study.GetContents('Distribution Factors Results (SYM).ElmRes')
    elmres = res_list[0] if res_list else None
    app.PrintPlain(f"ElmRes:{elmres}")
    results = elmres.GetContents('*.ElmRes')
    comres = app.GetFromStudyCase('ComRes')
    ptdf_path = os.path.join(base_path,"PTDFs")
    os.makedirs(base_path,exist_ok=True)
    for r in results:
        comres.pResult = r
        comres.iopt_exp = 6 #CSV file
        comres.iopt_sep = 0  #Define own separator
        comres.col_Sep = ";"
        safe_name = r.loc_name.replace(" ","_").replace("-","")
        filename = os.path.join(ptdf_path,f"{safe_name}.csv")
        comres.f_name = filename
        comres.iopt_csel = 0 # Export all variables
        comres.iopt_locn = 1 #Header: Name
        comres.ciopt_head = 2 # Short description
        rc = comres.Execute()
        app.PrintPlain(f"Exported result: {r} -> filename: {filename}, rc: {rc}")
    end = time.time()
    app.PrintPlain(f"Execution time: {end - start:.4f} seconds")
if __name__ == "__main__":
    main()