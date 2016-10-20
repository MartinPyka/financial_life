'''
Created on 03.10.2016

@author: martin
'''
# standard libraries
import os
import imp
import platform

# third-party libraries
from  jinja2 import Template

# own libraries
from financial_life.reports import sl

path_template = '..{sl}templates{sl}html'.format(sl=sl)


def report(simulation, style = 'standard', output_dir = 'report'):
    """ This is a generic report function that renders html-templates
    defined by the style-argument. 
    
    'style' refers to a template-folder in '../templates/html'. A
    file render.py must be included in the template-folder with a method
    'render(simulation, output_dir)' that does the job. New html-templates
    can be easily added by creating new subfolders in '../templates/html/'
    with html files and a render.py
    """    
    cwd = os.path.dirname(os.path.realpath(__file__))
    template_folder = cwd + sl + path_template + sl + style + sl
    
    render_module = imp.load_source('render', template_folder + 'render.py')
    render_module.render(simulation, output_dir)