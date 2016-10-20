'''
Created on 30.03.2016

@author: martin
'''

import xml.etree.ElementTree as ET
import re

def import_colors():
    group_tag = '{http://www.w3.org/2000/svg}g'
    rect_tag = '{http://www.w3.org/2000/svg}rect'
    
    color_file = '/home/martin/ownCloud/Software/credit/misc/colors.svg'
    
    tree = ET.parse(color_file)
    root = tree.getroot()
    layer = root.find(group_tag)
    groups = layer.findall(group_tag)
    
    colorgroups = []
    
    for group in groups:
        schemas = group.findall(group_tag)
        colorgroup = []
        for schema in schemas:
            rects = schema.findall(rect_tag)
            colors = []
            for rect in rects:
                colors.append(re.search('#[0-9a-f]{6}', rect.attrib['style']).group())
            colorgroup.append(colors)
        colorgroups.append(colorgroup)
    
    print(colorgroups)

colors = [
          [
           ['#9e63e7', '#b283ed', '#cbaaf5', '#e0ccf9', '#884dd7', '#6925c5', '#5512b0', '#430596'], 
           ['#6463e6', '#8483ec', '#aaa9f5', '#cccbf9', '#4c4dd7', '#2526c4', '#1113b0', '#050596'], 
           ['#629ce6', '#83b1eb', '#a8caf5', '#cbdef9', '#4b8bd7', '#256dc3', '#105ab0', '#054696'], 
           ['#62cae5', '#82d5eb', '#a7e4f5', '#cbeef9', '#4bbbd6', '#25a4c3', '#0f92b0', '#057896'], 
           ['#62e4df', '#82eae6', '#a6f5f2', '#cbf9f8', '#4ad6ce', '#25c3ba', '#0fb0a5', '#05968f']
          ], 
          [
           ['#c6e662', '#d2eb83', '#e2f5a8', '#edf9cb', '#b7d74b', '#a0c325', '#8cb010', '#749605'], 
           ['#e6e462', '#ebeb83', '#f5f4a8', '#f8f9cb', '#d7d34b', '#c3c025', '#b0ab10', '#969305'], 
           ['#e5a962', '#ebbb82', '#f5d1a7', '#f9e5cb', '#d6944b', '#c37825', '#b0630f', '#965205'], 
           ['#e47a62', '#ea9682', '#f5b6a6', '#f9d5cb', '#d6634a', '#c34125', '#b02a0f', '#962005'], 
           ['#e36269', '#e98287', '#f4a6aa', '#f9cbcc', '#d64954', '#c32530', '#b00f1c', '#96050e']
          ], 
          [
           ['#a2a2a2', '#b5b5b5', '#cdcdcd', '#e2e2e2', '#8f8f8f', '#747474', '#5f5f5f', '#4d4d4d']
          ], 
          [
           ['#7a68b3', '#9080c1', '#aa9dd3', '#c1b7df', '#6b5e97', '#4f4378', '#392b68', '#261953'], 
           ['#6876b2', '#808dc0', '#9ca6d3', '#b6bddf', '#5d6997', '#434e77', '#2a3768', '#192553'], 
           ['#6797b2', '#81a8be', '#9bbfd3', '#b6cfdf', '#5d8396', '#426577', '#295368', '#193f53'], 
           ['#68b0b0', '#80bdbe', '#9ad2d3', '#b6dddf', '#5d9595', '#427777', '#286867', '#195353'], 
           ['#68af9e', '#81bdae', '#99d3c5', '#b6dfd6', '#5d9486', '#427769', '#286857', '#195345']
          ], 
          [
           ['#aeb267', '#bcbe81', '#d1d39b', '#dcdfb6', '#95965d', '#767742', '#676829', '#515319'], 
           ['#b2a267', '#beb281', '#d3c79b', '#dfd8b6', '#96895d', '#776b42', '#685a29', '#534619'], 
           ['#b08168', '#be9580', '#d3ad9a', '#dfc5b6', '#956f5d', '#775342', '#683d28', '#532c19'], 
           ['#af6869', '#bd8181', '#d39999', '#dfb7b6', '#945d5e', '#774244', '#68282a', '#53191a'], 
           ['#ad697a', '#bb818f', '#d19aa8', '#dfb6bf', '#945c6c', '#774251', '#68283a', '#531928']
          ]
         ]

no_colors = len(colors[0])