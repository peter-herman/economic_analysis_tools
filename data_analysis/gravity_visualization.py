__author__ = "Peter Herman"
__project__ = "gme.estimate"
__created__ = "05-16-2018"

import pandas as pd
from gme import EstimationModel
from typing import List
import matplotlib.pyplot as plt
from scipy.stats import norm
from numpy import nan
import math


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

    Returns: (dictionary) A dictionary listing the sectors for which estimates are missing for each variable.
    """
    if estimation_model.results_dict is None:
        raise ValueError("results_dict does not exist. Must estimate model first.")

    results_dict = estimation_model.results_dict
    dict_key = results_dict.keys()
    coeff_df = pd.DataFrame(columns=variables)
    no_estimates = dict()
    for var in variables:
        coefficients = []
        no_estimates[var] = list()
        for key in dict_key:
            try:
                coefficients.append(results_dict[key].params[var])
            except:
                no_estimates[var].append(key)
        coeff_df[var] = pd.Series(coefficients)

    if rename_variables is not None:
        coeff_df.rename(columns=rename_variables, inplace=True)
    coeff_df.plot(kind='density', bw_method=bandwidth, subplots=True)

    if path is not None:
        plt.savefig(path)







def gravity_coefficient_error_bars(estimation_model,
                                   variables:list = [],
                                   path:str = None,
                                   fig_dimensions:tuple = None,
                                   subplot_titles:dict = None,
                                   confidence_interval:float = 0.95,
                                   color_significance:float = None,
                                   freq_xticks:int = 1,
                                   xtick_plots:List[tuple]=[],
                                   numeric_sectors = False,
                                   legend_in_subplot = False,
                                   styles:dict = None):
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
        confidence_interval: (float) The confidence level to use for the bars. Default is 0.95. Use 0 to turn off error
            bars
        color_significance: (float) Optional. If supplied, colors insignificant values differently based on significance
            level. Defualt in None, which does not color estimates differently.
        freq_xticks:  (int) The frequency with which labels are displayed for xticks. Default is 1, which displays every
            tick. Values greater than one reduce the frequency (e.g. 5 would include every fifth label). To include no
            labels, use a value of zero. Unless the value is zero, the first and last labels are always included.
        styles: (dict) Optional. Dictionary to specify certain color and formatting options. Can replace default options
            by supplying a dictionary containing some or all of the following keys (default values are given). See
            matplotlib documentation for valid color and format selections.
                {'est_color':'blue',        # Color of main coefficient estimate points
                 'est_fmt':'.',             # Format of main estimate points
                 'est_bar_color':'blue',    # Color of main confidence interval error bar
                 'insig_color':'red',       # Color of insignificant estimate points (if color_significance specified)
                 'insig_fmt':'x',           # Format of insignificant estimate points
                 'insig_bar_color':'red',   # Color of insignificnat error bars
                 'zero_color':'k',          # Color of zero line
                 'zero_fmt':'--'}           # Format of zero line

    Returns: Produces a plot and, if specified, saves one or more plots at the secified file paths.

    '''
    # ---
    # Prep additional Args
    # ---
    style = {'est_color':'C0',
             'est_fmt':'.',
             'est_bar_color':'C0',
             'insig_color':'C3',
             'insig_fmt':'x',
             'insig_bar_color':'C3',
             'zero_color':'k',
             'zero_fmt':'--'}
    # Replace default values with user values.
    if styles is not None:
        for key, field in styles.items():
            style[key]=field


    # ---
    # Prep Data
    # ---

    # Unpack some values
    sector_var_name = estimation_model.estimation_data._meta_data.sector_var_name

    # Collect Estimates and reformat DataFrame to multi-index dataframe
    estimates = estimation_model.combine_sector_results()
    # ToDo: make this robust to sector names containing '_' (E.g. split on the last '_' or identify specific strings (coeff, pvalue, etc.)
    multi_col_names = [col.split('_') for col in estimates.columns]
    modified_col_names = list()
    for col in multi_col_names:
        if len(col)>2:
            col = ["_".join(col[0:-2]), col[-1]]
        if numeric_sectors:
            try:
                col = [int(col[0]),col[1]]
            except ValueError:
                try:
                    col = [float(col[0],col[1])]
                except:
                    raise ValueError('Sector cannot be treated as numeric.')
        modified_col_names.append(tuple(col))
    multi_index = pd.MultiIndex.from_tuples(modified_col_names, names=['sector', 'param'])
    estimates.columns = multi_index

    # Reshape Sectors Long
    param_info = estimates.unstack().reset_index()
    param_info.columns = [sector_var_name,'param','variable','value']

    # Reshape estimate type wide
    param_info = param_info.pivot_table(values = 'value',index = [sector_var_name,'variable'], columns='param').reset_index()

    # Get a vector of sectors
    sector_list = pd.DataFrame({sector_var_name:param_info[sector_var_name].unique()})
    num_sectors = sector_list.shape[0]

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

    # Check for the right number of subplots
    if legend_in_subplot:
        if not len(plot_scheme)>len(variables):
            raise ValueError("fig_dimensions does not specify enough subplots to include legend in separate plot")
    if len(plot_scheme)<len(variables):
        raise ValueError("fig_dimensions does not specify enough subplots for specified variables.")

    #Remove extra plots if necessary
    if len(plot_scheme)>len(variables):
        extra_plots = len(plot_scheme)-len(variables)
        if legend_in_subplot:
            extra_plots = extra_plots-1
        for num in range(extra_plots):
            # Return last value in list
            del_plot = plot_scheme.pop()
            fig.delaxes(axs[del_plot[0], del_plot[1]])

    # Add plotting information
    for num in range(len(variables)):
        plot_scheme[num].append(variables[num])
        plot_scheme[num].append(num)
    if legend_in_subplot:
        plot_scheme[-1].append('legend_subplot')
        plot_scheme[-1].append(len(plot_scheme)-1)


    # Create each subplot
    for row, col, var_name, num in plot_scheme:
        # Grab subplot axis
        if n_rows < 2 or n_cols < 2:
            # In cases where there are not multiple rows or columns, 2 dimension coordinates do not work.
            ax = axs[num]
        else:
            ax = axs[row, col]

        # If not a legend subplt, create actual coefficient plot
        if var_name != 'legend_subplot':
            var_info = param_info.loc[param_info['variable']==var_name,:].copy()
            if var_info.shape[0]<num_sectors:
                var_info = sector_list.merge(var_info, how = 'left', on = sector_var_name)
            var_info.sort_values(by=[sector_var_name], inplace = True)

            # Plot Significant Estimates
            if color_significance is None:
                if confidence_interval==0:
                    coeff_points = ax.errorbar(var_info[sector_var_name], var_info['coeff'], None,
                                               fmt=style['est_fmt'], ecolor=style['est_bar_color'],
                                               mec=style['est_color'], mfc=style['est_color'])
                else:
                    coeff_points = ax.errorbar(var_info[sector_var_name], var_info['coeff'], z_value*var_info['stderr'],
                                               fmt = style['est_fmt'], ecolor = style['est_bar_color'],
                                               mec=style['est_color'], mfc=style['est_color'])

            # Plot significance in different colors
            if color_significance is not None:
                insignificant_coeffs = var_info.loc[var_info['pvalue']>(1-color_significance),:]
                significant_coeffs = var_info.copy()
                significant_coeffs.loc[significant_coeffs['pvalue']>(1-color_significance),'coeff']=nan
                if confidence_interval==0:
                    coeff_points = ax.errorbar(significant_coeffs[sector_var_name], significant_coeffs['coeff'], None,
                                               fmt=style['est_fmt'], ecolor=style['est_bar_color'],
                                               mec=style['est_color'], mfc=style['est_color'])
                    insig_points = ax.errorbar(insignificant_coeffs[sector_var_name], insignificant_coeffs['coeff'],
                                               None,
                                               mfc=style['insig_color'], mec=style['insig_color'],
                                               fmt=style['insig_fmt'], ecolor=style['insig_bar_color'])
                else:
                    coeff_points = ax.errorbar(significant_coeffs[sector_var_name], significant_coeffs['coeff'],
                                               z_value * significant_coeffs['stderr'],
                                               fmt=style['est_fmt'], ecolor=style['est_bar_color'],
                                               mec=style['est_color'], mfc=style['est_color'])
                    insig_points = ax.errorbar(insignificant_coeffs[sector_var_name], insignificant_coeffs['coeff'],
                                z_value*insignificant_coeffs['stderr'],
                                               mfc=style['insig_color'], mec=style['insig_color'],
                                               fmt=style['insig_fmt'], ecolor=style['insig_bar_color'])
                if not legend_in_subplot:
                    plt.legend([coeff_points, insig_points],[ "Significant at {} level".format(color_significance),
                                                          "Not significant at {} level".format(color_significance)])

            ax.plot(var_info[sector_var_name], [0]*len(var_info[sector_var_name]), linestyle = style['zero_fmt'], color = style['zero_color'])
            ax.set_title(subplot_titles[var_name])

        # If a Legend Subplot, create legend
        if var_name == 'legend_subplot':
            ax.set_axis_off()
            ax.legend([coeff_points, insig_points],[ "Significant at {} level".format(color_significance),
                                                          "Not significant at {} level".format(color_significance)], loc='center')
        # Set x labels for last row
        ax.set_xticks(sector_list[sector_var_name].tolist())
        if (row < (n_rows-1)) and ((row, col) not in xtick_plots):
            plt.setp(ax.get_xticklabels(), visible=False)
        else:
            if freq_xticks ==0:
                plt.setp(ax.get_xticklabels(), visible=False)
            if freq_xticks >0:
                # Determine spacing of labels
                # spacing = math.ceil((num_sectors - 1) / (freq_xticks - 1) - 1)
                # spacing = round(num_sectors/(freq_xticks-1))
                # Fill list of xticks with empty strings and selected labels
                xtick_labels = num_sectors * ['']
                for i in range(0, 1 + math.floor(num_sectors / freq_xticks)):
                    try:
                        xtick_labels[i * (freq_xticks)] = sector_list.loc[i * (freq_xticks), sector_var_name]
                    except:
                        pass
                xtick_labels[0] = sector_list.loc[0, sector_var_name]
                xtick_labels[-1] = sector_list.loc[(num_sectors-1),sector_var_name]
                ax.set_xticklabels(xtick_labels)



        # if no_xticks:
        #     plt.setp(ax.get_xticklabels(), visible=False)




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

    return fig, axs