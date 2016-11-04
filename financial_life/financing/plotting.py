'''
Created on 30.03.2016

@author: martin
'''
#standard libraries
from datetime import timedelta

# custom libraries
from matplotlib.pyplot import *
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# own libraries
from .colors import colors, no_colors
from financial_life.calendar_help import Bank_Date

#ion()

# indices for colors in the colors-list
C_cold_colors = 0
C_warm_colors = 1
C_format_date = '%d.%m.%Y'

def bank_account(*reports):
    fig = figure(figsize=(16, 13))
    plot_stack_mult_abs(['input_cum', 'output_cum'], *reports, 
                    color_themes = [C_warm_colors, C_cold_colors], 
                    color_offset = 1)
    title('Demands on the account')
    return fig

def summary(*reports):
    """ Summary plot for all reports """
    
    fig = figure(figsize=(16, 13))
    ax_date = subplot(3,2,1)
    plot_stack_abs('saving_abs', *reports, color_theme = C_warm_colors, color_offset = 0)
    title('Wealth')
    
    subplot(3,2,2, sharex = ax_date)
    plot_stack_abs('debt_abs', *reports, color_theme = C_cold_colors, color_offset = 0)
    title('Debts')
    
    subplot(3,2,3, sharex = ax_date)
    plot_stack_mult_abs(['input_cum', 'output_cum'], *reports, 
                        color_themes = [C_warm_colors, C_cold_colors], 
                        color_offset = 1)
    title('Input and output')
    
    subplot(3,2,4, sharex = ax_date)
    plot_stack_abs('debtpayment_cum', *reports, color_offset = 1)
    title('Yearly payments')
    
    ax_winloss = subplot(3,2,5, sharex = ax_date)
    plot_stack_cum('win_cum', *reports, color_theme = C_warm_colors, color_offset = 2)
    title('Cumulated win')
    
    subplot(3,2,6, sharex = ax_date, sharey = ax_winloss)
    plot_stack_cum('cost_cum', *reports, color_offset = 2)
    title('Cumulated costs')
    plt.tight_layout()
    return fig

def summary_img(*reports, target = './', figsize = (10, 5), dpi = 100, prefix=''):
    """ creates a series of images and stores them in the target directory """
    
    data = {}
    
    fig = figure(figsize = figsize)
    plot_stack_abs('saving_abs', *reports, color_theme = C_warm_colors, color_offset = 0)
    title('Wealth')
    fig.savefig(target + prefix + 'wealth.jpg', dpi = dpi)
    plt.close(fig)
    data['img_wealth'] = target + prefix + 'wealth.jpg'
    
    fig = figure(figsize = figsize)
    plot_stack_abs('debt_abs', *reports, color_theme = C_cold_colors, color_offset = 0)
    title('Debts')
    fig.savefig(target + prefix + 'debts.jpg', dpi = dpi)
    plt.close(fig)
    data['img_debts'] = target + prefix + 'debts.jpg'
    
    fig = figure(figsize = figsize)
    plot_stack_mult_abs(['input_cum', 'output_cum'], *reports, 
                        color_themes = [C_warm_colors, C_cold_colors], 
                        color_offset = 1)
    title('Input and output')
    fig.savefig(target + prefix + 'io_money.jpg', dpi = dpi)
    plt.close(fig)
    data['img_io_money'] = target + prefix + 'io_money.jpg'

    fig = figure(figsize = figsize)
    plot_stack_abs('debtpayment_cum', *reports, color_offset = 1)
    title('Yearly payments')
    fig.savefig(target + prefix + 'debtpayment.jpg', dpi = dpi)
    plt.close(fig)
    data['img_debtpayment'] = target + prefix + 'debtpayment.jpg'
    
    fig = figure(figsize = figsize)
    plot_stack_cum('win_cum', *reports, color_theme = C_warm_colors, color_offset = 2)
    title('Cumulated win')
    fig.savefig(target + prefix + 'win_cum.jpg', dpi = dpi)
    plt.close(fig)
    data['img_win_cum'] = target + prefix + 'win_cum.jpg'
    
    fig = figure(figsize = figsize)
    plot_stack_cum('cost_cum', *reports, color_offset = 2)
    title('Interests')
    fig.savefig(target + prefix + 'cost_cum.jpg', dpi = dpi)
    plt.close(fig)
    data['img_cost_cum'] = target + prefix + 'cost_cum.jpg'
    
    return data
     

def extract_data(semantic, *reports, color_theme = C_cold_colors, color_offset = 0):
    """ helping function that extracts the dates and data from the reports """
    X = []
    Y = []
    c = []
    # create cost plots
    for j, r in enumerate(reports):
        X = X + [[d.timestamp() for d in r.date]]
        Y = Y + [[r.get(k) for k in r.semantics(semantic)]]
        
        c = c + [colors[color_theme][j % no_colors][i+color_offset] for i, k in enumerate(r.semantics(semantic))]
    
    return X, Y, c

def add_labels(semantic, *reports, color_theme = C_cold_colors, color_offset = 0):
    """ routine that adds labels to the plot in order to add a legend """
    # these empty plots are needed as stack plot does not support labels for legends. bit of 
    # a hack from http://stackoverflow.com/questions/14534130/legend-not-showing-up-in-matplotlib-stacked-area-plot
    for j, r in enumerate(reports):
        for i, k in enumerate(r.semantics(semantic)):
            plot([], [], 
                 color=colors[color_theme][j % no_colors][i+color_offset], 
                 label=r.name + ': ' + k,
                 linewidth=10)
            
def plot_stack_generic(X, Y, c, semantic, *reports, color_theme = C_cold_colors, color_offset = 0):
    """ generic function for plotting stacks """
    # bring the data together
    dates, data = join_data(X, Y)
    
    # format the dates to a readable format
    str_dates = [Bank_Date.fromtimestamp(d).strftime(C_format_date) for d in dates]
    
    add_labels(semantic, *reports, color_theme = color_theme, color_offset = color_offset)

    if len(data) > 0:
        stackplot(dates, data, colors = c)
    else:
        # if data is empty, plot at least zeros to make this plot more complete
        plot(dates, np.zeros(len(dates)))
    
    xticks(dates, str_dates, rotation=45)

def remove_nones(X):
    """ Removes all Nones from a list and replaces them by zero """
    return [[[0. if v is 'None' else v for v in d] for d in data] for data in X]

def add_zeros(X, Y):
    """ add zeros at the beginning and end to prevent interpolation in join_data
    from stacking to much up """
    for x in X:
        x.insert(0, x[0] - 1)
        x.append(x[-1] + 1)

    for data in Y:
        for d in data:
            d.insert(0, 0.)
            d.append(0.)
    
    return X, Y

def plot_stack_abs(semantic, *reports, color_theme = C_cold_colors, color_offset = 0):
    """ Creates a stacked plot with cumulated sums for a given semantic """ 
    X, Y, c = extract_data(semantic, *reports, color_theme = color_theme, color_offset = color_offset)
    Y = remove_nones(Y)
    X, Y = add_zeros(X, Y)

    # create the generic plot
    plot_stack_generic(X, Y, c, semantic, *reports, color_theme = color_theme, color_offset = color_offset)
    legend(loc = 'upper right', fancybox=True, framealpha=0.4, prop={'size':10})
    
def plot_stack_mult_abs(semantics, *reports, color_themes, color_offset = 0):
    """ Creates a stacked plot with cumulated sums for a given semantic """ 
    for semantic, color_theme in zip(semantics, color_themes):
        plot_stack_abs(semantic, *reports, color_theme = color_theme, color_offset = color_offset)

def plot_stack_cum(semantic, *reports, color_theme = C_cold_colors, color_offset = 0):
    """ Creates a stacked plot with cumulated sums for a given semantic """ 
    X, Y, c = extract_data(semantic, *reports, color_theme = color_theme, color_offset = color_offset)
    Y = remove_nones(Y)
    # add zeros only at the beginning    
    for x in X:
        x.insert(0, x[0] - 1)
    
    for data in Y:
        for d in data:
            d.insert(0, 0.)
                
    # create the cumulated sum
    Y = [np.cumsum(np.array(yi), 1) if yi else [] for yi in Y]

    plot_stack_generic(X, Y, c, semantic, *reports, color_theme = color_theme, color_offset = color_offset)
    legend(loc = 'upper left', fancybox=True, framealpha=0.4, prop={'size':10})    
    
def join_data(dates_list, data_list):
    """ This functions makes heterogenous time series data align
    with one time series axis 
    dates   : list of date-lists
    data    : list of data-lists_lock
    
    Returns:
        dates, and data, but this time, data shares the same
        date-points
    """
    # first get all unique dates from every sublist and make one list out of them
    rdates = sorted(list(set([date for sublist in dates_list for date in sublist])))
    rdata = []
    
    # go through each vector and interpolate data if necessary
    for dates, data_vecs in zip(dates_list, data_list):
        for data in data_vecs:
            if len(data) > 0:
                rdata.append(np.interp(rdates,dates, data).tolist())
            else:    # if data is empty, then just create a zero-length vector
                rdata.append(np.zeros(len(rdates)))
    return rdates, rdata
                    