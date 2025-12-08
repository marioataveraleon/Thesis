import powerfactory as pf
import pf_utils
import runner

def main():
   app = pf_utils.connect_to_powerfactory()
   project = pf_utils.get_project(app)
   all_study_cases = pf_utils.get_all_study_cases(project)

   desired_studycase = pf_utils.select_study_case(all_study_cases,"SMIB","SG","E1")
   runner.run_simulation(app,desired_studycase)



if __name__ == "__main__":
    main()