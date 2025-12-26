from collections.abc import Iterable

def connect_to_powerfactory():
    import powerfactory as pf
    app = pf.GetApplication()
    if not app:
        raise RuntimeError("Could not connect to PowerFactory.")
    app.ClearOutputWindow()
    app.PrintPlain("=== PF Automation OK ===")
    return app


def get_project(app):
    """
    Return the active PowerFactory project.
    """
    project = app.GetActiveProject()
    if project is None:
        raise RuntimeError("No active PowerFactory project found.")
    return project


def get_all_study_cases(app):
    """
    Return all study cases (IntCase objects) inside all grids and technologies.
    Skips the folder 'Task Automation'.
    """

    study_cases = []   # ← LISTA donde acumulamos todo
    number_of_sc = 0

    study_cases_folder = app.GetProjectFolder('study')
    if not study_cases_folder:
        return study_cases
    # first level (grids: SMIB, IEEE9, etc.)
    study_cases_all_grids = study_cases_folder.GetContents()
    for grid in study_cases_all_grids:
        # skip this folder
        if "Task Automation" in grid.loc_name:
            continue

        # second level (technologies: SG, GFL, GFM)
        technologies = grid.GetContents()

        for tech in technologies:

            # third level: actual study cases (IntCase)
            cases = tech.GetContents('*.IntCase')

            # append each case into the list
            for c in cases:
                study_cases.append(c)
                number_of_sc +=1
    app.PrintPlain(f"Existing study cases: {number_of_sc}")

    return study_cases





def activate_study_case(study_case_obj):
    """
    Activate the provided study case (pass object, NOT name).
    """
    if study_case_obj is None:
        raise ValueError("activate_study_case received None")
    study_case_obj.Activate()



def get_simulation_objects(study_case):
    """
    Return all RMS simulation objects (ComSim) inside a study case.
    """
    sims = study_case.GetContents("*.ComSim", 1)
    if sims is None:
        return []
    return sims
def _get_sc_path(sc):
    """
    Return the full path of a study case, e.g.:
    'Study Cases.SMIB.SG.E1 LoadStep'
    """
    try:
        return sc.GetFullName()
    except Exception:
        # Fallback: at least return its name
        return sc.loc_name


def select_study_cases(app,study_cases,system = None,inv_type = None,event = None):
    """ 
    Return one study case matching by system (SMIB,IEEE9,etc) by inverter
    type (SG,GFL,GMF) and by event (E1,E2,E3)
    def normalize is a function to transform a string into list
    if the argument passed is none it leave is as none
    """
    def normalize(x):
        if x is None:
            return None
        if isinstance(x,str):
            return [x]
        return x
    system  = normalize(system)
    inv_type = normalize(inv_type)
    event = normalize(event)

    matches = []

    for study_case in study_cases:
        full_path = _get_sc_path(study_case)

        name = study_case.loc_name
        if system is not None and not any(s in full_path for s in system):
            continue
        if inv_type is not None and not any (t in full_path for t in inv_type):
            continue
        if event is not None and not any(e in name for e in event):
            continue
        matches.append(study_case)
    if len(matches) == 0:
        raise RuntimeError(
            f"No study case found for filters: "
            f"System: {system}, Type: {inv_type}, Event: {event}"
        )
    app.PrintPlain(f"Returning studycases for: {system},{inv_type},{event}")
    app.PrintPlain(f"number of studycases that matched the search: {len(matches)}")

    return matches
