import os,re,glob, time
from datetime import datetime
import pf_utils

#Helpers

def _safe_filename(text: str, maxlen: int = 120) -> str:
    """Convert any string to a safe name for the folder to be created properly"""

    text = (text or "").strip()
    text = text.replace("\\", "_").replace("/", "_").replace(":", "_")
    text = re.sub(r"[^\w\-\.]+", "_", text) 
    text = re.sub(r"_+", "_", text)
    return text[:maxlen].strip("_")

def _build_case_folder(tesis_root:str, study_case)->str:
    """
    Create a folder inside the Results folder contained in the tesis folder
    
    :param tesis_root: route to the tesis folder
    :type repo_root: str
    :param study_case: studycase name which will be stored
    :return: folder
    :rtype: folder
    """
    results_root = os.path.join(tesis_root,"Results")
    sc_path = pf_utils._get_sc_path(study_case)
    technology = _get_tech_from_scpath(sc_path)
    folder_path = os.path.join(results_root,
                          _safe_filename(technology),
                          _safe_filename(study_case.loc_name))
    os.makedirs(folder_path,exist_ok=True)
    return folder_path


def _get_tech_from_scpath(sc_path:str)-> str:
    """
    Extract the technology from the short circuit path, the pattern is like:
    '...REE_GFL_E0...' or '...REE_GFM_Droop_E1...' etc.
    Returns 'GFL' 'GFD_Droop', etc.
    """
   
    m = re.search(r"REE[\\/]+([^\\/]+)",sc_path)
    if not m:
        return "UNKNOWN"
    return m.group(1)


def clear_pngs(app,folder:str):
    files = glob.glob(os.path.join(folder,"*.png"))
    app.PrintPlain(f"[clear_pngs] deleting {len(files)} in folder {folder}")
    for f in files:
        os.remove

def export_graphic_tab_as_png(app,folder:str)->list[str]:
    """
    Export all tabs type Graphic (Diagram/Plot) opened in the desktop to png. 
    
    :param app: Powerfactory app
    :param folder: folder to save the files
    :type folder: str
    :param frefix: 
    :type frefix: str
    :return: List od files saved as png
    :rtype: list[str]
    """
    desktop = app.GetDesktop()
    tabgroups = desktop.GetTabGroups()
    comwr = app.GetFromStudyCase("ComWr")
    comwr.iopt_rd = "*.png"
    if not comwr:
        app.PrintError("No ComWr founded in the active study case")
        return []
    
    exported = []
    used_names = set() # evita el overwrite de titulos repetidos
    for tabgroup in tabgroups:
        n =tabgroup.GetTabCount()
        for i in range (n):
            tab_type = tabgroup.GetTabType(i)
            if tab_type != 0: # si es 0, es un diagram
                continue
            tab_object = tabgroup.GetTabObject(i)
            if not tab_object:
                continue
            title = tabgroup.GetTabTitle(i)
            
            base = _safe_filename(title) if title else f"GraphicTab_{i:02d}"
            name = base

            #evitar sobreescribir tabs

            candidate = name
            k = 1
            while candidate.lower() in used_names:
                k+=1
                candidate = f"{name}__{k}"
            used_names.add(candidate.lower())
            fpath = os.path.join(folder,f"{candidate}.png")
            rc = comwr.ExportGraphicTab(tab_object,fpath)
            if rc == 0:
                exported.append(fpath)
            else: 
                app.PrintPlain("Export failed")

def export_studycase_results_to_csv(app,studycase,folderpath):
    
    comRes = app.GetFromStudyCase('ComRes')
    comRes.iopt_exp = 6
    comRes.iopt_csel = 1
    setattr(comRes, "from", -13)
    comRes.to = 20
    sc_name =_safe_filename(studycase.loc_name) + ".csv"
    comRes.f_name =os.path.join(folderpath,sc_name)

    comRes.Execute()


