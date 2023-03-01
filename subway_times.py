from datetime import datetime, timedelta
import re
import requests

N_ITEMS = 4

def get_headsign_abbr(headsign: str) -> str:
    headsign = re.sub(r'[aeiou]{1}[aeiouw]{1}', '', headsign)
    headsign = re.sub(r'[aeiou]{1}', '', headsign)

    return headsign.upper()

def get_subway_times_dict(station_id: str, n_entries: int) -> dict:
    r = requests.get(f'https://demo.transiter.dev/systems/us-ny-subway/stops/{station_id}')
    data = r.json()
    headsign_res = {}

    for s in data['stopTimes']:
        if s['headsign'] not in headsign_res:
            headsign_res[s['headsign']] = []
        if len(headsign_res[s['headsign']]) < n_entries:
            headsign_res[s['headsign']].append(s)

    all_lst = []
    for _, s_lst in headsign_res.items():
        for s in s_lst:
            all_lst.append(s)
    headsign_res['ALL'] = all_lst
    
    return headsign_res

def get_subway_times_strings(subway_times: list, str_tmpl, print_headsign = False) -> list[str]:
    res_strs = []
    count = 0
    for s in subway_times:
        try:
            arr_time = datetime.fromtimestamp(int(s['arrival']['time']))
        except:
            arr_time = datetime.fromtimestamp(int(s['departure']['time']))

        delta = arr_time - datetime.now()
        if - delta > timedelta(seconds=60) or delta >= timedelta(minutes=60):
            continue

        delta = delta // timedelta(minutes=1)
        if delta <= 0:
            delta_str = 'ARR'
        else:
            delta_str = str(delta)
        
        route = s['trip']['route']['id']

        if not print_headsign:
            cur_str = str_tmpl.format(route, delta_str)
        else:
            heading = get_headsign_abbr(s['headsign'].split(' ')[0])
            cur_str = str_tmpl.format(heading, route, delta_str)
        res_strs.append(cur_str)
        count += 1

    return res_strs

if __name__ == '__main__':
    str_tmpl = r'({}) {}'
    str_tmpl_all = r'{}: ({}) {}'

    for h, s_lst in get_subway_times_dict('125', N_ITEMS).items():
        print(f'Headsign: {h}')
        if h == 'ALL':
            for s in get_subway_times_strings(s_lst, str_tmpl_all, True):
                print(s)
        else:
            for s in get_subway_times_strings(s_lst, str_tmpl):
                print(s)


