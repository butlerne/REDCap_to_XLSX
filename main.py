import sys
import os
import pandas as pd
from datetime import datetime
from datetime import timedelta
from requests import post

# Can't put variable TOKEN on public repo.
URL = 'https://redcap.dartmouth.edu/api/'

payload = {'token': TOKEN, 'format': 'json', 'content': 'record', 'type': 'eav'}


class Weeks(object):
    def __init__(self, week, day_1, day_2, day_3, day_4, day_5, day_6, day_7):
        self.week = week
        self.day_1 = day_1
        self.day_2 = day_2
        self.day_3 = day_3
        self.day_4 = day_4
        self.day_5 = day_5
        self.day_6 = day_6
        self.day_7 = day_7


def create_weeks(participant):
    payload2 = {'records': participant, 'forms': 'mysaferx_registration_form'}
    payload.update(payload2)
    response = post(URL, data=payload)
    data = response.json()
    print

    for a in data:
        if 'field_name' in a and a['field_name'] == 'sd3':
            # Unless b is made global, it'll sometimes throw UnboundLocalError. Unsure if best practice.
            global b
            b = datetime.strptime(a['value'], '%Y-%m-%d').date()

    week_01 = [b + timedelta(days=x) for x in range(0, 7, 1)]
    week_02 = [b + timedelta(days=x) for x in range(7, 14, 1)]
    week_03 = [b + timedelta(days=x) for x in range(14, 21, 1)]
    week_04 = [b + timedelta(days=x) for x in range(21, 28, 1)]
    week_05 = [b + timedelta(days=x) for x in range(28, 35, 1)]
    week_06 = [b + timedelta(days=x) for x in range(35, 42, 1)]
    week_07 = [b + timedelta(days=x) for x in range(42, 49, 1)]
    week_08 = [b + timedelta(days=x) for x in range(49, 56, 1)]
    week_09 = [b + timedelta(days=x) for x in range(56, 63, 1)]
    week_20 = [b + timedelta(days=x) for x in range(133, 140, 1)]

    count = [Weeks("Week 01", *week_01), Weeks("Week 02", *week_02), Weeks("Week 03", *week_03),
             Weeks("Week 04", *week_04), Weeks("Week 05", *week_05), Weeks("Week 06", *week_06),
             Weeks("Week 07", *week_07), Weeks("Week 08", *week_08), Weeks("Week 09", *week_09),
             Weeks("Week 20", *week_20)]
    week_dict = dict([(c.week, [c.day_1, c.day_2, c.day_3, c.day_4, c.day_5, c.day_6, c.day_7]) for c in count])
    return week_dict


def in_week(part_weeks):
    now = [datetime.now().date()]
    for d, e in part_weeks.items():
        if set(e).isdisjoint(now) is False:
            return d


def main_menu():
    os.system('clear')

    print "Welcome,\n"
    print "Please choose a function:"
    print "5. Uncollected Screen Excel Sheet"
    print "\n0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)

    return


def exec_menu(choice):
    os.system('clear')
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print "Invalid selection, please try again.\n"
            menu_actions['main_menu']()
    return


def menu5():
    week_dict = {}
    # Simply bc our records are # starting at 3001.
    for t in range(3001, 3013, 1):
        payload2 = {'records': t, 'forms': 'urine_toxicology'}
        payload.update(payload2)
        response = post(URL, data=payload)
        data = response.json()
        list_dates = []
        missed_weeks = []
        # Variable data returns a list of very redundant dictionaries.
        for i in data:
            for k, v in i.items():
                # if len(v) == 10 makes sure that the unicode dict value is a date.
                if k == 'value' and len(v) == 10:
                    w = datetime.strptime(v, '%Y-%m-%d').date()
                    list_dates.append(w)
        #Goes out to function create_weeks which is reused in other menus
        #Creates a list of "Week" objects that represent the dates of participation
        for d, e in create_weeks(t).items():
            #Checks the dates of participation against the list of submitted urine screens
            if set(e).isdisjoint(list_dates) is True:
                #Appends to a list if submitted urine screen week is NOT in participation weeks
                missed_weeks.append(d)
        missed_weeks.sort()
        week_dict[t] = missed_weeks
        t += 1
    df = pd.DataFrame.from_dict({k: pd.Series(v) for k, v in week_dict.iteritems()}).transpose()
    print df
    q_print = raw_input("Would You Like to Print? (Y/N)")
    if q_print == "Y":
        writer = pd.ExcelWriter('missing_utox.xlsx', engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
    print "9. Back"
    print "0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return


def back():
    menu_actions['main_menu']()


def program_exit():
    sys.exit()


menu_actions = {
    'main_menu': main_menu,
    '1': menu1,
    '2': menu2,
    '3': menu3,
    '4': menu4,
    '5': menu5,
    '9': back,
    '0': program_exit,
}

if __name__ == '__main__':
    main_menu()

