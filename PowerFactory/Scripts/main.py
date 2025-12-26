import importlib
import pf_utils
import runner
importlib.reload(pf_utils)
importlib.reload(runner)

sim_config = None
system = ["REE"]
technology = ["SG"] 
event = ["E0","E1"]
def main():
   app = pf_utils.connect_to_powerfactory()
   all_study_cases = pf_utils.get_all_study_cases(app)
   desired_studycases= pf_utils.select_study_cases(app,all_study_cases,
                                                   system,
                                                   technology,
                                                   event)
   
   for sc in all_study_cases:
       app.PrintPlain(sc)
   #runner.run_simulations(app, desired_studycases,sim_config)




if __name__ == "__main__":
    main()