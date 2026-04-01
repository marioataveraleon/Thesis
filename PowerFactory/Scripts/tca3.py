import pf_utils
import importlib
import pandas as pd
import numpy as np
import os
import tca
import re

def run_hca():
    return 
def export_results(app,filename):
    study = app.GetActiveStudyCase()
    res_list = study.GetContents('DER Capacity.ElmRes')
    elmres = res_list[0] if res_list else None
    app.PrintPlain(f"res_list: {res_list}")
    app.PrintPlain(f"elmres: {elmres}")
    comres = app.GetFromStudyCase('ComRes')
    results_path = r"C:\Users\PF-WS-008\Desktop\Tesis\ResultsPhase3"
    hca_path = os.path.join(results_path,"HCA")
    os.makedirs(results_path,exist_ok=True)
    comres.pResult = elmres
    comres.iopt_exp = 6 #CSV file
    comres.iopt_sep = 0  #Define own separator
    comres.col_Sep = ";"
    safe_name = filename.replace(" ","_").replace("-","")
    filename = os.path.join(hca_path,f"{safe_name}.csv")
    comres.f_name = filename
    comres.iopt_csel = 0 # Export all variables
    comres.iopt_locn = 1 #Header: Name
    comres.ciopt_head = 2 # Short description
    rc = comres.Execute()
    app.PrintPlain(f"Exported result: {elmres} -> filename: {safe_name}, rc: {rc}")
    

def main():
    base_path = r"C:\Users\UI450907\Desktop\TE RWEST\Tesis\Phase3Results"
    app = pf_utils.connect_to_powerfactory()
    # Relevante netzobjekte lesen
    terminals,lines,trafos = tca.get_relevant_objects(app)

    for line in lines:
        line.outserv = 0
    for trafo in trafos:
        trafo.outserv = 0
    app.PrintPlain(f"{len(lines)} Lines on Service & {len(trafos)} Transformers on service")
    
    #Get SetSelect
    study = app.GetActiveStudyCase()
    sets = study.GetContents('*.SetSelect')
    bus_set = None
    for s in sets:
        if s.loc_name == "Set - Hosting Sites (Terminals)":
            bus_set = s
            app.PrintPlain(f"Set Select Terminals founded!! :) : {bus_set}")
            break
    if bus_set is None:
        app.PrintPlain("No Set Select Busbars founded, creating object...")
        bus_set = study.CreateObject('SetSelect','Set - Hosting Sites (Terminals)')
        app.PrintPlain(f"Hosting Terminals Created: {bus_set}")
        bus_set.iused = 30 #Hosting Capacity analysis
        bus_set.iusedSub = 1 #Busbars
        bus_set.AddRef(terminals) # Add the terminals to the setselect objects
    #Get HCA 
    hca = app.GetFromStudyCase('ComHostcap')
    app.PrintPlain(f"HCA: {hca}")
    hca.selObj = bus_set
    hca.objective = 0 # DER Analysis
    hca.iSysTyp = 0 # AC LoadFlow
    hca.iLdfType = 0 #Standard Loadflow
    hca.iopt_lodcons = 1 # Thermal/loading constraints
    hca.constChkScope = 1 # Whole system
    rc = hca.Execute()
    if rc == 0:
        app.PrintPlain(f"HCA Succesfully Executed: {rc}")
    
    #Get to export results
    export_results(app,"Base Case")


    #Run the analysis HCA with automated contingencies
    for line_out in lines:
        case_name = re.sub(r"_+", "_", f"{line_out.loc_name}_Cnt".replace("-", "_").replace(" ", "_"))
        app.PrintPlain(f"Line out: {line_out.loc_name}")
        line_out.outserv = 1 # Line out of service
        rc = hca.Execute()
        if rc == 0:
            app.PrintPlain(f"HCA Succesfully executed: {rc}")
            export_results(app,case_name)
        line_out.outserv = 0 # Reactivating the line
        app.PrintPlain(f"Line on:{line_out.loc_name}")
    
    for trafo_out in trafos:
        case_name = re.sub(r"_+", "_", f"{trafo_out.loc_name}_Cnt".replace("-", "_").replace(" ", "_"))
        app.PrintPlain(f"Trafo out: {trafo_out.loc_name}")
        trafo_out.outserv = 1 # Line out of service
        rc = hca.Execute()
        if rc == 0:
            app.PrintPlain(f"HCA Succesfully executed: {rc}")
            export_results(app,case_name)
        trafo_out.outserv = 0 # Reactivating the line
        app.PrintPlain(f"Line on:{trafo_out.loc_name}")

        






if __name__ == "__main__":
    main()