import powerfactory as pf
import pf_utils
def main():
    app = pf.GetApplication()
    if  not app:
        raise RuntimeError("No se pudo conectar con powerfactory")
    app.ClearOutputWindow()
    app.PrintPlain("=== Test PowerFactory-Python OK ===")
    project = pf_utils.get_project(app)
    app.PrintPlain(project)
    all_study_cases = pf_utils.get_all_study_cases(project)
    
    for sc in all_study_cases:
        app.PrintPlain(sc.loc_name)




if __name__ == "__main__":
    main()