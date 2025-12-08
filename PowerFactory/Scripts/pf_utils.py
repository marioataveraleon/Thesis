
import powerfactory

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


def get_all_study_cases(project):
    """
    Return all study cases (IntCase objects) in the project.
    Searches recursively inside the 'Study Cases' folder.
    """
    # Get ALL objects under Study Cases (recursive)
    objects = project.GetContents('Study Cases.*', 1)
    if not objects:
        return []

    # Filter only IntCase objects
    study_cases = [obj for obj in objects if obj.GetClassName() == 'IntCase']
    return study_cases


def activate_study_case(app, study_case_obj):
    """
    Activate the provided study case (pass object, NOT name).
    """
    if study_case_obj is None:
        raise ValueError("activate_study_case received None")

    app.ActivateStudyCase(study_case_obj)
    return study_case_obj


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


def select_study_case(study_cases,system,inv_type,event):
    """ 
    Return one study case matching by system (SMIB,IEEE9,etc) by inverter
    type (SG,GFL,GMF) and by event (E1,E2,E3)

    """
    matches = []

    for study_case in study_cases:
        full_path = _get_sc_path(study_case)
        name = study_case.loc_name
        if system is not None and system not in full_path:
            continue
        if inv_type is not None and inv_type not in full_path:
            continue
        if event is not None and event not in name:
            continue
        matches.append(study_case)
    if len(matches) == 0:
        raise RuntimeError(
            f"No study case found for filters: "
            f"System: {system}, Type: {inv_type}, Event: {event}"
        )
    if len(matches) > 1:
        names = ", ".join(sc.loc_name for sc in matches)
        raise RuntimeError(
            f"More than one study case matches filters "
            f"(system={system}, inv_type={inv_type}, event={event}): {names}"
        )

    return matches[0]

def get_simulation_objects(study_case):
    """
    Return all RMS simulation objects (ComSim) inside a study case.
    """
    sims = study_case.GetContents("*.ComSim", 1)
    if sims is None:
        return []
    return sims