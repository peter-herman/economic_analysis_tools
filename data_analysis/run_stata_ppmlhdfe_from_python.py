__Author__ = "Peter Herman"
__Project__ = "ntm_ave_analysis"
__Created__ = "April 28, 2020"
__Description__ = ''' '''

import subprocess
import pandas as pd

def stata_ppmlhdfe(do_file_path:str,
                       data_path:str,
                       fixed_effects:list,
                       trade_var:str,
                       grav_vars:list,
                       results_path:str,
                       stata_path,
                       data_subset_path:str = None):
    '''
    Create and run a ppmlhdfe regression in Stata in-line in python.

    :param do_file_path: (str) File path at which to create a do file for running the stata regression. Should have
        extension ".do".
    :param data_path: (str) File path for a .dta data file for use in the regression.
    :param fixed_effects: (list[list[str]]) A list of lists specifying the columns to use as fixed effects (same format as
        gme.EstimationModel) For example: [['importer', 'year'], ['exporter', 'year'], ['importer','exporter']]
    :param trade_var: (str) Column to use as the dependant variable.
    :param grav_vars: (list[str]) Columns to use as dependent gravity variables.
    :param results_path: (str) Path for creating a dataset (.dta) of stata results
    :param stata_path: (str) Path for the computer's Stata executable.
    :param data_subset_path: (str) Path to save the subset of the data used for the estimation (e.g. without missing values). 
        Path can be a .dta or .csv file type. The default is None, which does not save the data subset.

    :return: (pd.DataFrame) A dataframe of estimation results from Stata. Also writes a .do file and results .dta to the
        disk.

    Example:
    stata_results = stata_ppmlhdfe(do_file_path="D:\\work\\Peter_Herman\\projects\\ntm_ave_analysis\\economic_analysis_tools/data_analysis/test_stata.do",
                    data_path="G:\\data\\MRL 332 (2019-2020)\\estimations\\MRL_modeling_v2\\results_v2b\\DELETE_stata_testing_data.dta",
                    fixed_effects=[['importer', 'Item', 'year'], ['exporter', 'Item', 'year']],
                    trade_var='trade_value',
                    results_path="D:\\work\\Peter_Herman\\projects\\ntm_ave_analysis\\economic_analysis_tools\\data_analysis\\stata_test_results",
                    grav_vars=['international', 'ln_distance', 'contiguity', 'common_language', 'agree_pta',
                               'member_eu_joint', 'colony_ever'],
                    stata_path="C:\Program Files\Stata16\StataMP-64.exe")
    '''
    # Create do file
    create_hdfe_do_file(do_file_path=do_file_path,
                        data_path=data_path,
                        fixed_effects=fixed_effects,
                        trade_var=trade_var,
                        grav_vars=grav_vars,
                        results_path=results_path)
    # Run do file
    run_do_file(do_file = do_file_path,
                stata_path=stata_path)
    # Load and return the results
    if not results_path.endswith('dta'):
        results_path_temp = results_path+'.dta'
    stata_results = pd.read_stata(results_path_temp)
    return stata_results

def create_hdfe_do_file(do_file_path:str,
                        data_path:str,
                        fixed_effects:list,
                        trade_var:str,
                        results_path:str,
                        grav_vars:list,
                        data_subset_path:str = None):
    with open(do_file_path, "w") as do_file:
        # Specify Using Data
        do_file.write('use "{}"\n'.format(data_path))
        absorb_names = list()
        # Create FE identifiers
        for fe_profile in fixed_effects:
            fe_name = "_".join(fe_profile)
            absorb_names.append(fe_name)
            do_file.write("egen {}=group({})\n".format(fe_name, ' '.join(fe_profile)))
        # PPMLHDFE command
        do_file.write("ppmlhdfe {} {}, absorb({})\n".format(trade_var, " ".join(grav_vars), " ".join(absorb_names)))
        if data_subset_path is not None:
            do_file.write("keep if e(sample)\n")
            if data_subset_path.endswith(".dta"):
                do_file.write('save "{}", replace \n')
            else:
                do_file.write('export delimited using "{}", replace \n')
        # Save results
        do_file.write('parmest, saving("{}", replace) stars(0.1 0.05 0.01)\n'.format(results_path))

def run_do_file(do_file, stata_path:str = 'stata', args:list=None):
    # Set up do-file information [stata command or exe path, 'do'  process, do file]
    cmd = [stata_path, "do", do_file]
    # Add additional args in necessary (unlikely)
    if args:
        [cmd.append(arg for arg in args)]
    # Run do-file
    subprocess.call(cmd)
    return None







