import powerfactory
import pf_utils

def run_simulation(app, study_case):
    """
    Activate the given study case and run its RMS simulation.

    Assumptions:
    - The study case already contains exactly one relevant ComSim
      (RMS time-domain simulation) to be executed.
    """

    # 1) Activate the study case
    pf_utils.activate_study_case(app, study_case)
    app.PrintPlain(f"[runner] Activated study case: {study_case.loc_name}")

    # 2) Get all simulation objects (ComSim) inside this study case
    sim_objects = pf_utils.get_simulation_objects(study_case)

    if not sim_objects:
        raise RuntimeError(
            f"[runner] No RMS simulation (ComSim) found in study case '{study_case.loc_name}'."
        )

    # For now, we simply take the first ComSim
    sim = sim_objects[0]
    app.PrintPlain(f"[runner] Running RMS simulation: {sim.loc_name}")

    # 3) Execute the simulation
    rc = sim.Execute()
    app.PrintPlain(f"[runner] Simulation finished with return code: {rc}")

    return rc
