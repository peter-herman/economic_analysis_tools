__author__ = "Peter Herman"
__project__ = "gme.estimate"
__created__ = "05-16-2018"

import pandas as pd
from gme import EstimationModel
import matplotlib.pyplot as plt
from typing import List
import matplotlib.pyplot as plt
from scipy.stats import norm



def coefficient_kd_plot(estimation_model:EstimationModel,
                        variables: List[str],
                        path: str = None,
                        bandwidth: float = 0.5,
                        rename_variables: dict = None):
    """
    Produce kernel density plots of parameter estimates across different sectors in the results dictionary.

    Args:
        estimation_model: gme.EstimationModel
            An estimated EstimationModel with more than one sector.
        variables: List(str)
            A list of model covariates for which to plot kernel densities.
        path: (optional) str
            A path and file name at which to save the plot.
            Can end in the following file types for example: pdf, svg, and png.
        bandwidth: float
            Specify the bandwidth for the density plots. The default is 0.5.
        rename_variables: (optional)
            A dictionary of alternative variable names to use in the plot.
            For example {'original_name':'new_name}

    Returns: None
    """
    if estimation_model.results_dict is None:
        raise ValueError("results_dict does not exist. Must estimate model first.")

    results_dict = estimation_model.results_dict
    dict_key = results_dict.keys()
    coeff_df = pd.DataFrame(columns=variables)
    for var in variables:
        coefficients = []
        for key in dict_key:
            coefficients.append(results_dict[key].params[var])
        coeff_df[var] = pd.Series(coefficients)

    if rename_variables is not None:
        coeff_df.rename(columns=rename_variables, inplace=True)
    coeff_df.plot(kind='density', bw_method=bandwidth, subplots=True)

    if path is not None:
        plt.savefig(path)






def gravity_coefficient_error_bars(estimation_model:EstimationModel,
                           variables:list = [],
                           path:str = None,
                           fig_dimensions:tuple = None,
                           subplot_titles:dict = None,
                           delete_subplot:list = [],
                           confidence_interval:float = 0.95,
                           no_xticks:bool = True):
    '''
    Plot Gravity coefficient estimates from GME with error bars for confidence intervals.

    Args:
        estimation_model: (gme.EstimationModel) An estimated gravity model. Makes the most sense if it is
            sector_by_sector.
        variables: (list[str]) A list of variables to be plotted. Default uses EstimationModel rhs_vars.
        path:  (str or List[str]) A file path or list of file paths to save image. Supplying multiple paths permits the
            creation of multiple image types (e.g. png, eps, etc.)
        fig_dimensions: (tuple[int, int]) Specify the layout for the subfigures of the format (# rows, # columns)
        subplot_titles: (dict) Optional: Dictionary that allows for the use of subplot titles other than the variable
            names. Dictionary should take the form dict[variable_name] = 'alternative_title' for each variable.
        delete_subplot: (list[tuple[int, int]]) Optional: Delete specified subplot or plots. Useful if the grid of
            subplots has more cels than are neccessary. For example, if plotting 5 figures in a 3x2 grid, include (0,0)
            to delete the row=0, col=0 cell, leaving a blank space instead of empty axes.
        confidence_interval: (float) The confidence level to use for the bars. Default is 0.95.
        no_xticks:  (bool) If True, no x-axis labels are included. Can be useful when sector names are two long to be
            properly displayed olong axis.

    Returns: Produces a plot and, if specified, saves one or more plots at the secified file paths.

    '''
    # ---
    # Prep Data
    # ---

    # Unpack some values
    sector_var_name = estimation_model.estimation_data.meta_data.sector_var_name

    # Collect Estimates and reformat DataFrame to multi-index dataframe
    estimates = estimation_model.combine_sector_results()
    multi_col_names = [tuple(col.split('_')) for col in estimates.columns]
    multi_index = pd.MultiIndex.from_tuples(multi_col_names, names=['sector', 'param'])
    estimates.columns = multi_index

    # Reshape Sectors Long
    param_info = estimates.unstack().reset_index()
    param_info.columns = [sector_var_name,'param','variable','value']

    # Reshape estimate type wide
    param_info = param_info.pivot_table(values = 'value',index = [sector_var_name,'variable'], columns='param').reset_index()

    # ---
    # Create Plot
    # ---

    # Prepare Plot Inputs
    if len(variables) == 0:
        variables = estimation_model.specification.rhs_var
    if fig_dimensions is None:
        fig_dimensions = (len(variables),1)
    n_rows = fig_dimensions[0]
    n_cols = fig_dimensions[1]
    if subplot_titles is None:
        subplot_titles = dict()
        for var in variables:
            subplot_titles[var] = var
    z_value =  norm.ppf(1 - (1-confidence_interval)/2)

    # Create Master Plot
    fig, axs = plt.subplots(nrows=n_rows, ncols=n_cols, sharex=True, sharey=False)

    # Define coordinates for each subplot
    plot_scheme = [[row, col] for row in range(n_rows) for col in range(n_cols)]
    if len(plot_scheme) != len(variables):
        raise ValueError("\n Supplied dimensions ({} subplots) does not match number of variables ({})".format(
            len(plot_scheme), len(variables)))
    # Assign a varaible to each sub plot coordinates
    for num in range(len(plot_scheme)):
        plot_scheme[num].append(variables[num])

    # Create each subplot
    for row, col, var_name in plot_scheme:
        var_info = param_info.loc[param_info['variable']==var_name,:].copy()
        var_info.sort_values(by=[sector_var_name], inplace = True)
        ax = axs[row, col]
        # ax.locator_params(nbins=4)
        ax.errorbar(var_info[sector_var_name], var_info['coeff'], z_value*var_info['stderr'], fmt = '.', ecolor = 'k')
        ax.plot(var_info[sector_var_name], [0]*len(var_info[sector_var_name]), linestyle = '--', color = 'orange')
        ax.set_title(subplot_titles[var_name])
        if no_xticks:
            plt.setp(ax.get_xticklabels(), visible=False)


    # Delete unused plots in grid
    if len(delete_subplot)!=0:
        for coord in delete_subplot:
            fig.delaxes(axs[coord[0],coord[1]])

    fig.tight_layout(pad=1.0)
    for ax in axs.flat:
        ax.set(xlabel=sector_var_name, ylabel='Estimate')
    # for ax in axs.flat:
    #     ax.label_outer()
    plt.show()

    if path is not None:
        if isinstance(path, str):
            path = [path]
        for image in path:
            image_type = image.partition(".")[-1]
            fig.savefig(image, format = image_type, bbox_inches = "tight")


