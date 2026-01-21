
import pf_utils
import export_utils
import importlib
importlib.reload(export_utils)
DEFAULT_SIM_CONFIG = {
    "tstop": 20.0, #time in seconds
    "dtgrd": 10    # example: integration step
}

def run_simulation(app, study_case,sim_config = None):
    """
    Activate the given study case and run its RMS simulation.

    Assumptions:
    - The study case already contains exactly one relevant ComSim
      (RMS time-domain simulation) to be executed.
    """

    # 1) Activate the study case
    pf_utils.activate_study_case(study_case)
    app.PrintPlain(f"[runner] Activated study case: {pf_utils._get_sc_path(study_case)}")

    # 2) Get all simulation objects (ComSim) inside this study case
    sim_objects = pf_utils.get_simulation_objects(study_case)
    iniConditions = study_case.GetContents("*.ComInc",1)
    iniConditions = iniConditions[0]

    if not sim_objects:
        raise RuntimeError(
            f"[runner] No RMS simulation (ComSim) found in study case '{study_case.loc_name}'."
        )

    
    sim = sim_objects[0]
    #Assigning the attributes to the simulation
    cfg = {**DEFAULT_SIM_CONFIG, **(sim_config or {})}
    
    for attr,value in cfg.items():
        if hasattr(sim,attr):
            setattr(sim,attr,value)
        else:
            app.PrintPlain(f"Warning: ComSim in '{study_case.loc_name}' has no attribute'{attr}'")

    # 3) Execute the simulation
    app.PrintPlain(f"[runner] Running Initial Conditions")
    iniConditions.Execute()
    rc = sim.Execute()
    app.PrintPlain(f"[runner] Simulation finished with return code: {rc}")

    return rc

def run_simulations(app,studycases,sim_config: dict | None = None,tesis_root:str = ""):


    """
    Docstring for run_multiple_simulations
    
    :param app: PowerFactory Application
    :param studycases: List of study cases where the simulations will be runned
    :param sim_config: Dictionary containing the simulation attribute
    :Dictionary sim_config: dict | None
    """
    app.PrintPlain(f"Running simulations for: {len(studycases)} studycases")
    for studycase in studycases:
        folderpath = export_utils._build_case_folder(tesis_root,studycase)
        export_utils.clear_pngs(app,folderpath)
        rc = run_simulation(app,studycase,sim_config)
        if rc == 0:
            export_utils.export_graphic_tab_as_png(app,folderpath)
            export_utils.export_studycase_results_to_csv(app,studycase,folderpath)

