import powerfactory


def get_project(app):
    """Return the active project."""
    project = app.GetActiveProject()
    if project is None:
        raise Exception("No active project found.")
    return project


def get_study_case(app, rel_path_or_name: str):
    """
    Find a study case using its relative path under 'Study Cases'
    or a pattern with wildcards.
    Example: 'SMIB\\SG\\E1 LoadStep' or '*E1 LoadStep*'
    """
    sc_list = app.GetFromStudyCase(f"Study Cases.{rel_path_or_name}")
    if not sc_list:
        raise Exception(f"Study case not found: {rel_path_or_name}")
    return sc_list[0]

def get_all_study_cases(project):
    all_study_cases= project.GetContents('*.IntCase',1)
    return all_study_cases

def get_element(project, pf_class: str, name: str):
    """
    Generic object finder inside 'Network Model'.

    pf_class : PowerFactory class, e.g. 'ElmTerm', 'ElmSym', 'ElmLod', ...
    name     : object name, e.g. 'Bus1', 'SG1', 'Load1'
    """
    path = f"Network Model.{pf_class}.{name}"
    objs = project.GetContents(path)
    if not objs:
        raise Exception(f"Element not found: {path}")
    return objs[0]


# Optional nice wrappers for readability:

def get_bus(project, name: str):
    return get_element(project, "ElmTerm", name)


def get_generator(project, name: str):
    return get_element(project, "ElmSym", name)  # or ElmInfeeder if you use that


def get_load(project, name: str):
    return get_element(project, "ElmLod", name)
