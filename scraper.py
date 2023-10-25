import requests
from bs4 import BeautifulSoup
import csv
import regex as re
import argparse

def process_time(str_value):

    if not str_value: return 0

    pair = str_value.split(':')
    minutes, seconds = map(int, pair)
    total_seconds = minutes * 60 + seconds

    return total_seconds

def process_occ_goals_time(str_value):
    """
        0-3/04:05

        to values 

        0, 3, 245 

        (245 seconds)
    """


    # Use regular expressions to split the string into three parts
    parts = re.split(r'[-/]', str_value)

    value1 = int(parts[0])
    value2 = int(parts[1])

    return value1, value2, process_time(parts[2])

def analyze_report(url, team1, team2):
    """
        Return a list of:

        - total game time

        - total penalty minutes for team 1  
        - total penalty minutes for team 2  

        - penalty minutes for team 1 in period 1  
        - penalty minutes for team 1 in period 2  
        - penalty minutes for team 1 in period 3  
        - penalty minutes for team 1 in period OT  
        - penalty minutes for team 2 in period 1  
        - penalty minutes for team 2 in period 2  
        - penalty minutes for team 2 in period 3  
        - penalty minutes for team 2 in period OT  

        - team 1 goals in period 1
        - team 1 goals in period 2
        - team 1 goals in period 3
        - team 1 goals in period OT
        - team 1 shots in period 1
        - team 1 shots in period 2
        - team 1 shots in period 3
        - team 1 shots in period OT
        
        - team 2 goals in period 1
        - team 2 goals in period 2
        - team 2 goals in period 3
        - team 2 goals in period OT
        - team 2 shots in period 1
        - team 2 shots in period 2
        - team 2 goals in period 3
        - team 2 shots in period OT

        - team 1 power plays 5v4 occurences
        - team 1 power plays 5v4 goals
        - team 1 power plays 5v4 time
        - team 1 power plays 5v3 occurences
        - team 1 power plays 5v3 goals
        - team 1 power plays 5v3 time
        - team 1 power plays 4v3 occurences
        - team 1 power plays 4v3 goals
        - team 1 power plays 4v3 time

        - team 2 power plays 5v4 occurences
        - team 2 power plays 5v4 goals
        - team 2 power plays 5v4 time
        - team 2 power plays 5v3 occurences
        - team 2 power plays 5v3 goals
        - team 2 power plays 5v3 time
        - team 2 power plays 4v3 occurences
        - team 2 power plays 4v3 goals
        - team 2 power plays 4v3 time

        - team 1 even strength 5v5 occurences
        - team 1 even strength 5v5 goals
        - team 1 even strength 5v5 time
        - team 1 even strength 4v4 occurences
        - team 1 even strength 4v4 goals
        - team 1 even strength 4v4 time
        - team 1 even strength 3v3 occurences
        - team 1 even strength 3v3 goals
        - team 1 even strength 3v3 time

        - team 2 even strength 5v5 occurences
        - team 2 even strength 5v5 goals
        - team 2 even strength 5v5 time
        - team 2 even strength 4v4 occurences
        - team 2 even strength 4v4 goals
        - team 2 even strength 4v4 time
        - team 2 even strength 3v3 occurences
        - team 2 even strength 3v3 goals
        - team 2 even strength 3v3 time
        
        - team 1 goaltender 1 time
        - team 1 goaltender 2 time
        - team 1 empty net time 

        - team 2 goaltender 1 time
        - team 2 goaltender 2 time
        - team 2 empty net time
    """


    data = []

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve {url}. Status code:", response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Step 1: finding penalty minutes

    # Find the first table that starts with the specified row
    penalty_table = None
    for table in soup.find_all('table'):
        # Find the first row in the table
        first_row = table.find('tr')
        if first_row and 'PENALTY SUMMARY' in first_row.get_text():
            penalty_table = table
            break
    
    section = 0
    penalties = [ [0, 0, 0, 0], [0, 0, 0, 0] ]
    for row in penalty_table.find_all('tr'):

        row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]

        if len(row_data) == 6:
            section += 1
            continue 

        if len(row_data) == 10:

            period = 4 if row_data[1] not in '123' else int(row_data[1])

            penalties[section - 1][period - 1] += process_time(row_data[2])

    data += [sum(penalties[0]), sum(penalties[1])] + penalties[0] + penalties[1]
 
    # Step 2: finding period shots and goals

    # Find the first table that starts with the specified row
    period_table = None
    for table in soup.find_all('table'):
        # Find the first row in the table
        first_row = table.find('tr')
        if first_row and 'BY PERIOD' in first_row.get_text():
            period_table = table
            break

    section = 0
    goals_shots = [ [[0, 0, 0, 0], [0, 0, 0, 0]], [[0, 0, 0, 0], [0, 0, 0, 0]] ]       
    for row in period_table.find_all('tr'):

        row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]

        if len(row_data) != 5: 
            continue

        if row_data[0] == 'Per':
            section += 1
            continue
        
        if row_data[0] == 'TOT':
            continue

        period = 4 if row_data[0] not in '123' else int(row_data[0])
        goals = int(row_data[1])
        shots = int(row_data[2])

        goals_shots[section - 1][0][period - 1] += goals
        goals_shots[section - 1][1][period - 1] += shots

    data += goals_shots[0][0] +  goals_shots[0][1] +  goals_shots[1][0] +  goals_shots[1][1] 

    # Step 3: finding power plays 

    # Find the first table that starts with the specified row
    power_table = None
    for table in soup.find_all('table'):
        # Find the first row in the table
        first_row = table.find('tr')
        if first_row and 'POWER PLAYS' in first_row.get_text():
            power_table = table
            break
    
    power_plays = [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], 
                   [[0, 0, 0], [0, 0, 0], [0, 0, 0]]]
    section = 0
    for row in power_table.find_all('tr'):

        row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]

        if len(row_data) != 4:
            continue

        if row_data[0] == '5v4':
            section += 1
            continue

        for i, str_value in enumerate(row_data):

            if not str_value: continue

            occurences, goals, time = process_occ_goals_time(str_value)

            power_plays[section - 1][i][0] += occurences
            power_plays[section - 1][i][1] += goals
            power_plays[section - 1][i][2] += time

    data += power_plays[0][0] + power_plays[0][1] + power_plays[0][2] 
    data += power_plays[1][0] + power_plays[1][1] + power_plays[1][2] 

    # Step 4: finding even strength 

    # Find the first table that starts with the specified row
    even_table = None
    for table in soup.find_all('table'):
        # Find the first row in the table
        first_row = table.find('tr')
        if first_row and 'EVEN STRENGTH' in first_row.get_text():
            even_table = table
            break
    
    even_strength = [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], 
                     [[0, 0, 0], [0, 0, 0], [0, 0, 0]]]
    section = 0
    for row in even_table.find_all('tr'):

        row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]

        if len(row_data) != 4:
            continue

        if row_data[0] == '5v5':
            section += 1
            continue

        for i, str_value in enumerate(row_data[:-1]):

            if not str_value: continue

            occurences, goals, time = process_occ_goals_time(str_value)

            even_strength[section - 1][i][0] += occurences
            even_strength[section - 1][i][1] += goals
            even_strength[section - 1][i][2] += time


    data += even_strength[0][0] + even_strength[0][1] + even_strength[0][2] 
    data += even_strength[1][0] + even_strength[1][1] + even_strength[1][2]     

    # Step 5: finding goalkeeper data 

    # Find the first table that starts with the specified row
    goaltender_tables = []
    for table in soup.find_all('table'):
        # Find the first row in the table
        first_row = table.find('tr')
        if not first_row:
            continue 
        
        if (team1 in first_row.get_text().lower()) or (team2 in first_row.get_text().lower()):
            goaltender_tables.append(table)
    
    game_time = None
    goaltenders = [[0, 0], [0, 0]]
    analyzed_goaltenders = 0
    for row in goaltender_tables[0].find_all('tr'):

        row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]

        if row_data[0] == 'TEAM TOTALS' and game_time is None:
            game_time = process_time(row_data[4])
            continue

        if len(row_data) < 2: 
            continue

        # player numbers are between 1 and 98 inclusive
        if (row_data[1] != 'G') or (len(row_data[0]) > 2):
            continue

        goaltenders[analyzed_goaltenders // 2][analyzed_goaltenders % 2] += process_time(row_data[3])
        analyzed_goaltenders += 1

    # because of overtime empty net cant be negative
    data += goaltenders[0] + [max(3600 - sum(goaltenders[0]), 0)] + goaltenders[1] + [max(3600 - sum(goaltenders[1]), 0)]
    
    data = [game_time] + data

    return data
    
def analyze_league(url, min = 0, max = -1):

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to retrieve the webpage. Status code:", response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table rows (tr) with the specified structure
    target_data = []
    list_of_cells = [row.find_all('td') for row in soup.find_all('tr') if row.find_all('td')]
    max = len(list_of_cells) if max == -1 else max
    for cells in list_of_cells[min:max]:
        
        row_data = [cell.get_text(strip=True) for cell in cells]

        hometeam, otherteam = row_data[2].split('-')
        hometeam = hometeam.lower()
        otherteam = otherteam.lower()

        points1, points2 = row_data[3].split('-')

        changed_row_data = row_data[:2] + [hometeam, otherteam, points1, points2] + row_data[4:] 

        target_data.append(changed_row_data)

    links = [link.get('href') for link in soup.find_all('a') if 'http://www.nhl.com/scores/htmlreports' in link.get('href')]
    links = links[min:max]
    for i, link in enumerate(links):

        print(f"around {i/len(links) * 100:.2f}% completed")

        target_data[i].append(link)

        other_data = analyze_report(link, target_data[i][3], target_data[i][4])

        target_data[i] += other_data

    # Write the extracted data to a CSV file
    with open('output.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["id", "stage", "date", "hometeam", "otherteam", "points1", "points2", "scoretype", "location", "attendance", 
                             "reportlink", 

                             "total_gametime",

                             "penalty_tot1", "penalty_tot2",

                             "team_1_penalty_p1", "team_1_penalty_p2", "team_1_penalty_p3", "team_1_penalty_ot",
                             "team_2_penalty_p1", "team_2_penalty_p2", "team_2_penalty_p3", "team_2_penalty_ot", 

                             "team_1_goals_p1", "team_1_goals_p2", "team_1_goals_p3", "team_1_goals_ot",
                             "team_1_shots_p1", "team_1_shots_p2", "team_1_shots_p3", "team_1_shots_ot",
                             "team_2_goals_p1", "team_2_goals_p2", "team_2_goals_p3", "team_2_goals_ot",
                             "team_2_shots_p1", "team_2_shots_p2", "team_2_shots_p3", "team_2_shots_ot",

                             "team_1_pp_5v4_occ", "team_1_pp_5v4_goal", "team_1_pp_5v4_time",
                             "team_1_pp_5v3_occ", "team_1_pp_5v3_goal", "team_1_pp_5v3_time",
                             "team_1_pp_4v3_occ", "team_1_pp_4v3_goal", "team_1_pp_4v3_time",
                             "team_2_pp_5v4_occ", "team_2_pp_5v4_goal", "team_2_pp_5v4_time",
                             "team_2_pp_5v3_occ", "team_2_pp_5v3_goal", "team_2_pp_5v3_time",
                             "team_2_pp_4v3_occ", "team_2_pp_4v3_goal", "team_2_pp_4v3_time",

                             "team_1_es_5v5_occ", "team_1_es_5v5_goal", "team_1_es_5v5_time",
                             "team_1_es_4v4_occ", "team_1_es_4v4_goal", "team_1_es_4v4_time",
                             "team_1_es_3v3_occ", "team_1_es_3v3_goal", "team_1_es_3v3_time",
                             "team_2_es_5v5_occ", "team_2_es_5v5_goal", "team_2_es_5v5_time",
                             "team_2_es_4v4_occ", "team_2_es_4v4_goal", "team_2_es_4v4_time",
                             "team_2_es_3v3_occ", "team_2_es_3v3_goal", "team_2_es_3v3_time",

                             "team_1_goaltender_1_time", "team_1_goaltender_2_time", "team_1_empty_net_time",
                             "team_2_goaltender_1_time", "team_2_goaltender_2_time",  "team_2_empty_net_time"

                             ])
        for i, row_data in enumerate(target_data):

            csv_writer.writerow([i + min + 1] + row_data)

    print("Data has been successfully extracted and saved to 'output.csv'.")

def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('--nhl_league_link', type=str, default="https://hockey.sigmagfx.com/compseason/nhl/1819/games")

    parser.add_argument('--first_match', type=int, default=0)
    parser.add_argument('--last_match', type=int, default=-1, help='-1 means the actual last match (it later gets set to the maximum possible value)')

    args = parser.parse_args()

    return args

if __name__ == '__main__':

    args = get_args()
    analyze_league(args.nhl_league_link, min = args.first_match, max = args.last_match)