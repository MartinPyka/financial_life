'''
Created on 03.10.2016

@author: martin
'''

# standard libraries
import os
from datetime import datetime

# third-party libraries
from  jinja2 import Template

# own libraries
from financial_life.financing import plotting as plt
from financial_life.reports import sl

path_img = 'img'
path_accounts = 'accounts'

def render(simulation, output_dir = 'report'):
    print("Calling render function")
    template_folder = os.path.dirname(os.path.realpath(__file__))
    img_folder = output_dir + sl + path_img + sl
    accounts_folder = path_accounts + sl
    
    print('Template Folder: %s' % template_folder)
    # makedirs creates also all intermediate folders, therefore, we don't need
    # to create result_folder explicitely
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
    if not os.path.exists(output_dir + sl + accounts_folder):
        os.makedirs(output_dir + sl + accounts_folder)
            
    img_data = plt.summary_img(*simulation.reports('yearly'), target = img_folder)
    data = {}
    data['title'] = 'Kalkulation: ' + output_dir
    data['date'] = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    
    data.update(img_data)
    data.update(simulation.get_payments_unique_json())
    data.update(simulation.get_payments_regular_json())
    
    accounts = simulation.get_accounts_json()
    links = render_accounts(simulation, template_folder, output_dir, accounts_folder)
    
    # get_accounts_json and render_accounts iterate through simulation.account
    # therefore, the order in both is equal and we can add the link to the 
    # accounts json. this is not the safest way but I did not wanted to put
    # the get_accounts_json routine into this render-function 
    for a, l in zip(accounts['accounts'], links):
        a['link'] = l
    data.update(accounts)
    
    index_file = "index.html"
    with open(template_folder + sl + index_file, 'r') as f:
        content = f.read()
        t = Template(content)
        with open(output_dir + sl + index_file, 'w') as o:
            o.write(t.render(**data))
            
def render_accounts(simulation, template_folder, output_dir = 'report', accounts_folder = path_accounts):
    """ Renders for each account a detailed page with all account-specific
    data """
    accounts = simulation.accounts
    links = []
    
    # image folder for the account related pictures
    img_folder = output_dir + sl + accounts_folder + 'img' + sl
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)    
    
    for (i, a) in enumerate(accounts):
        account_name = a.name
        account_name.replace(' ', '_')
        prefix = 'account_details_%03i_%s' % (i, account_name)
        account_link = accounts_folder + prefix + '.html'
        print('Render %s' % account_link)
        links.append(account_link)
        
        data = {}
        data['account_name'] = a.name
        data['tables'] = a.get_report_json(interval='all')
        data['backlink'] = '..' + sl + 'index.html'
        img_data = plt.summary_img(a.report.yearly(), target = img_folder, prefix = prefix)
        data.update(img_data) 
        
        template_file = 'account_details.html'
        with open(template_folder + sl + template_file, 'r') as f:
            content = f.read()
            t = Template(content)
            with open(output_dir + sl + account_link, 'w') as o:
                o.write(t.render(**data))
    return links