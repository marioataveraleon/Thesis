import importlib
import pf_utils
import runner
import os
importlib.reload(pf_utils)
importlib.reload(runner)


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TESIS_ROOT = os.path.abspath(os.path.join(THIS_DIR,"..","..",".."))
if not os.path.isdir(os.path.join(TESIS_ROOT, "Results")):
    TESIS_ROOT = r"C:\Users\PF-WS-008\Desktop\Tesis"


sim_config = None
system = ["REE"]
technology = ["SG","GFL","GFM Droop","GFM VSM"] 
event = ["E0","E1","E2"]


def main():
   app = pf_utils.connect_to_powerfactory()
   all_study_cases = pf_utils.get_all_study_cases(app)
   desired_studycases= pf_utils.select_study_cases(app,all_study_cases,
                                                   system,
                                                   technology,
                                                   event)
   
   runner.run_simulations(app, all_study_cases,sim_config,TESIS_ROOT)




if __name__ == "__main__":
    main()