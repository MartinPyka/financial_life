""" All about housing """

import calendar_help as ch

import numpy as np
from calendar import monthrange
from datetime import date
from datetime import timedelta

def get_zinsen_pro_monat(monat, guthaben, rate, rate_date, zins):
    
    monatstage = float(monthrange(rate_date.year, rate_date.month)[1])
    
    neues_guthaben = guthaben
    zinsen1 = neues_guthaben * (zins / 12.) * (rate_date.day / monatstage)
    
    neues_guthaben += rate
    zinsen2 = neues_guthaben * (zins / 12.) * (1-(rate_date.day / monatstage))

    return (zinsen1 + zinsen2), neues_guthaben


def print_sparphase(result):
    print('Datum\t\tZahlung\t\tEntgelt\t\tZinsen\t\tKonto\t\tPunkte')
    for i in range(len(result['Zahlungen'])):
        print('%s\t%.2f\t\t%.2f\t\t%.2f\t\t%.2f\t%.3f' % (
                                      str(result['Datum'][i]), 
                                      result['Zahlungen'][i],
                                      result['Entgelt'][i],
                                      result['Zinsen'][i],
                                      result['Kontostand'][i],
                                      result['Punkte'][i]))
        
def print_kreditphase(result):
    print('Datum\t\tZahlung\t\tTilgung\t\tZinsen\t\tAgio\t\tVersicherung\tKredit')
    for i in range(len(result['Zahlungen'])):
        print('%s\t%.2f\t\t%.2f\t\t%.2f\t\t%.2f\t\t%.2f\t\t%.2f' % (
                                      str(result['Datum'][i]), 
                                      result['Zahlungen'][i],
                                      result['Tilgung'][i],
                                      result['Zinsen'][i],
                                      result['Agio'][i],
                                      result['Versicherung'][i],
                                      result['Kredit'][i],
                                      )
              )        

def report_spar(punkte, entgelt, zinslist, ratelist, neues_guthaben, datum, result):
    # budget related stuff
    result['Zahlungen'].append(float("{0:.2f}".format(np.sum(ratelist))))
    result['Zinsen'].append(float("{0:.2f}".format(np.sum(zinslist))))
    result['Kontostand'].append(float("{0:.2f}".format(neues_guthaben)))
    result['Entgelt'].append(float("{0:.2f}".format(entgelt)))
    result['Punkte'].append(float("{0:.3f}".format(punkte)))
    result['Datum'].append(datum)
    
def report_kredit(entgelt, zinslist, ratelist, neues_kredit, versicherungslist, datum, result):
    # budget related stuff
    result['Zahlungen'].append(float("{0:.2f}".format(np.sum(ratelist))))
    result['Zinsen'].append(float("{0:.2f}".format(np.sum(zinslist))))
    result['Kredit'].append(float("{0:.2f}".format(neues_kredit)))
    result['Agio'].append(float("{0:.2f}".format(entgelt)))
    result['Versicherung'].append(float("{0:.3f}".format(np.sum(versicherungslist))))
    result['Tilgung'].append(float("{0:.3f}".format(np.sum(ratelist) - np.sum(zinslist))))
    result['Datum'].append(datum)    

def simulate_day(punkte, raten_liste, tarif, entgelt, start_date, day, zinslist, ratelist, neues_guthaben, result):
    next_date = start_date + timedelta(days=day)
    days_per_year = 365 if monthrange(next_date.year, 2)[1] == 28 else 366
    
    for rate in raten_liste:
        # add rate to budget
        if (next_date.day == (rate['start'].day + 1)) and (next_date >= rate['start']):
            neues_guthaben += rate['betrag']
            ratelist.append(rate['betrag'])
            punkte += rate['betrag'] * tarif['C_POINT_PER_EUR']
    
    zinslist.append(neues_guthaben * (tarif['guthabenzins'] / days_per_year))
    punkte += tarif['C_POINT_PER_DAY']
    # if this is the beginning of a new year, add interests
    # to budget
    if (next_date.month == 12) and (next_date.day == 31):
        neues_guthaben += entgelt
        neues_guthaben = neues_guthaben + np.sum(zinslist)
        report_spar(punkte, entgelt, zinslist, ratelist, neues_guthaben, next_date, result)
        # setup for next year
        zinslist = []
        ratelist = []
        
    return neues_guthaben, zinslist, punkte, ratelist

def simulate_day_credit(raten_liste, tarif, entgelt, start_date, day, zinslist, ratelist, versicherungslist, neues_kredit, result):
    next_date = start_date + timedelta(days=day)
    neues_kredit += entgelt
    days_per_year = 365 if monthrange(next_date.year, 2)[1] == 28 else 366
    
    for rate in raten_liste:
        # add rate to budget
        if (next_date.day == (rate['start'].day + 1)) and (next_date >= rate['start']):
            neues_kredit -= min(neues_kredit, rate['betrag'])
            ratelist.append(min(neues_kredit, rate['betrag']))
    
    zinslist.append(neues_kredit * (tarif['darlehenszins'] / days_per_year))
    versicherungslist.append(neues_kredit * (tarif['versicherung'] / days_per_year))
    
    if (next_date.month == 12) and (next_date.day == 31):
        neues_kredit += np.sum(zinslist)
        neues_kredit += np.sum(versicherungslist)
        report_kredit(entgelt, zinslist, ratelist, neues_kredit, versicherungslist, next_date, result)
        # setup for next year
        zinslist = []
        ratelist = []
        versicherungslist = []
        
    return neues_kredit, zinslist, ratelist, versicherungslist

def get_kontoverlauf(
        guthaben, punkte, raten_liste, tarif,
        start_date = None, stop_date = None,
        subtract_entgelt = True):
    
    if not start_date:
        start_date = date(year=2017, month = 1, day = 1)
    
    if not stop_date:
        stop_date = date(year = 2017, month = 12, day = 31)
        
    days = (stop_date - start_date).days

    zinslist = []
    ratelist = []
    
    neues_guthaben = guthaben
    
    result = {'Zahlungen': [],
              'Zinsen': [],
              'Entgelt': [],
              'Kontostand': [],
              'Punkte': [],
              'Datum': []}
    
    # get through each day
    for day in range(days):
        neues_guthaben, zinslist, punkte, ratelist = simulate_day(
            punkte, 
            raten_liste,
            tarif, 
            tarif['entgelt'] if subtract_entgelt else 0, 
            start_date, 
            day, 
            zinslist, 
            ratelist, 
            neues_guthaben, 
            result)

    neues_guthaben += np.sum(zinslist)
    if subtract_entgelt:
        neues_guthaben += tarif['entgelt']
    report_spar(punkte, tarif['entgelt'], zinslist, ratelist, neues_guthaben, start_date + timedelta(days-1), result)
    
    return result, neues_guthaben, np.sum(zinslist), punkte, start_date + timedelta(day)

def get_time_range(
        guthaben, punkte, raten_liste, tarif,
        start_date = None):
    
    if not start_date:
        start_date = date(year=2017, month = 1, day = 1)

    zinslist = []
    ratelist = []
    
    neues_guthaben = guthaben
    
    result = {'Zahlungen': [],
              'Zinsen': [],
              'Entgelt': [],
              'Kontostand': [],
              'Punkte': [],
              'Datum': []
              }
    
    report_spar(punkte, tarif['entgelt'], zinslist, ratelist, neues_guthaben, start_date, result)
    
    current_date = start_date
    day = 0
    
    while punkte < tarif['C_POINT_LIMIT']:
        days_in_month = monthrange(current_date.year, current_date.month)[1] - current_date.day + 1
        for i in range(days_in_month):
            neues_guthaben, zinslist, punkte, ratelist = simulate_day(
                punkte,
                raten_liste,
                tarif,
                tarif['entgelt'],
                start_date,
                day,
                zinslist, 
                ratelist, 
                neues_guthaben, 
                result)
            day += 1
        current_date = current_date + timedelta(days=days_in_month)

    neues_guthaben += tarif['entgelt']
    report_spar(punkte, tarif['entgelt'], zinslist, ratelist, neues_guthaben, current_date + timedelta(days=-1), result)
    
    return result, neues_guthaben, np.sum(zinslist), punkte, current_date

def get_time_range_kredit(
        kredit, raten_liste, tarif, start_date = None):
    
    if not start_date:
        start_date = date(year=2017, month = 1, day = 1)

    zinslist = []
    ratelist = []
    versicherungslist = []
    
    neues_kredit = kredit
    
    result = {'Zahlungen': [],
              'Tilgung': [],
              'Zinsen': [],
              'Agio': [],
              'Versicherung': [],
              'Kredit': [],
              'Datum': []
              }
    
    report_kredit(neues_kredit * tarif['agio'], zinslist, ratelist, neues_kredit, versicherungslist, start_date, result)
    neues_kredit += neues_kredit * tarif['agio']
    
    current_date = start_date
    day = 0
    while neues_kredit > 0:
        days_in_month = monthrange(current_date.year, current_date.month)[1] - current_date.day + 1
        entgelt = 0
        for i in range(days_in_month):
            neues_kredit, zinslist, ratelist, versicherungslist = simulate_day_credit(
                raten_liste,
                tarif,
                0,
                start_date,
                day,
                zinslist, 
                ratelist,
                versicherungslist, 
                neues_kredit, 
                result)
            day += 1
        current_date = current_date + timedelta(days=days_in_month)

    neues_kredit += tarif['entgelt']
    report_kredit(entgelt, zinslist, ratelist, neues_kredit, versicherungslist, current_date + timedelta(days=-1), result)
    
    return result, neues_kredit, np.sum(zinslist), current_date

def calc_zwischenfinanzierung(
        guthaben, punkte, raten_spar, raten_kredit, tarif, start_date,
        log = True):
    
    if log:
        def printl(text):
            print(text)
    else:
        def printl(text):
            pass
        
    
    printl("Zwischenfinanzierung")
    r, k, z, p, d = get_time_range(
        guthaben = guthaben, 
        punkte = punkte, 
        raten_liste = raten_spar, 
        tarif = tarif, 
        start_date = start_date
        )
    
    if log:
        print_sparphase(r)
    
    printl("Warte-Phase")
    r, k, z2, p, d = get_kontoverlauf(
        guthaben = k+z, 
        punkte = p, 
        raten_liste = [],
        tarif = tarif, 
        start_date = d,
        stop_date = ch.add_month(d, tarif['wartemonate']),
        subtract_entgelt = False
        )
    
    if log:
        print_sparphase(r)
    
    last_date = r['Datum'][-1]
    
    months = ch.diff_months(start_date, last_date)
    years = months / 12.
    printl("Monate der Zwischenfinanzierung: %i" % months)
    
    zf_kosten = tarif['bausparsumme'] * tarif['darlehenszins'] * years 
    printl("Jaehrliche Kosten: %.2f EUR" % (tarif['bausparsumme'] * tarif['darlehenszins']))
    printl("Monatliche Kosten: %.2f EUR" % (tarif['bausparsumme'] * tarif['darlehenszins'] / 12))
    printl("Kosten der Zwischenfinanzierung: %.2f EUR" % zf_kosten)
    printl(" ")
    
    kredit = tarif['bausparsumme'] - k
    printl("Darlehenssumme: %.2f EUR" % kredit)
    
    r, k, z, d = get_time_range_kredit(
        kredit = kredit,
        raten_liste = raten_kredit,
        tarif = tarif,
        start_date = last_date)
    
    if log:
        print_kreditphase(r)
    
    sum_zinsen = np.sum(r['Zinsen'])
    sum_agio = np.sum(r['Agio'])
    sum_vers = np.sum(r['Versicherung'])
    sum_tilgung = np.sum(r['Tilgung'])
    sum_zahlung = np.sum(r['Zahlungen'])
    
    kredit_kosten = sum_zinsen + sum_agio + sum_vers
    gesamt_kosten = kredit_kosten + zf_kosten
    
    printl("Kosten")
    printl("Zinsen: %.2f EUR" % sum_zinsen)
    printl("Agio: %.2f EUR" % sum_agio)
    printl("Versicherung: %.2f EUR" % sum_vers)
    printl("Tilgung: %.2f EUR" % sum_tilgung)
    printl("Zahlung: %.2f EUR" % sum_zahlung)
    
    printl(" ")
    printl("Kosten des Kredites: %.2f EUR" % kredit_kosten)
    printl(" ")
    printl("Gesamtkosten: %.2f EUR" % gesamt_kosten)
    
    return gesamt_kosten   