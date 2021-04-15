###################################
##### Name: Chien-wei Tseng   #####
##### Uniqname: cwtseng       #####
###################################

import sqlite3
import plotly.graph_objects as go 

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'

# Part 1: Implement logic to process user commands
def process_command(command):
    '''Process input command(I called 'op' here, a.k.a operaiton) and return the result in array format

    Parameters
    ----------
    command: string
        input user command

    Returns
    -------
    results_arr list
        processed result in 2D array format
    '''
    # Check op(command) vaild
    valid = check_op_valid(command)

    # Replace op(command)
    final_op = create_final_op(command)

    # Create sql query
    final_q = create_final_query(final_op)

    # Execute sql query
    conn = sqlite3.connect('choc.sqlite')
    cur = conn.cursor()
    cur.execute(final_q)

    # Change to 2D array
    results_arr = []
    for idx, row in enumerate(cur):
        row = list(row)
        col = []
        for i in range(len(row)):
            col.append(row[i])
        results_arr.append(col)
    return results_arr

def load_help_text():
    ''' Load help text

    Parameters
    ----------
    None

    Returns
    -------
    string
        help text
    '''
    with open('Proj3Help.txt') as f:
        return f.read()

# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')
        if response == '':
            print()
            continue
        elif response == ' ':
            print()
            continue
        elif response == 'help':
            print(help_text)
            continue
        elif check_op_valid(response) == 1:
            results = process_command(response)
            final_op = create_final_op(response)
            print_format(results,final_op)
            plot_bar(results,final_op)
            continue
        elif check_op_valid(response) == 0 and response != 'exit':
            print(f"Command not recognized: {response}")
            print(f"")
            print(f"")
            continue
        elif response == 'exit':
            print('bye')

def check_op_valid(response):
    '''Check the command and options are all valid input

    Parameters
    ----------
    response: string
        input command

    Returns
    -------
    integer
        valid command or not, 1=valid, 0=not valid
    '''
    response_split = response.split()
    valid_op = {'bars':['country', 'region', 'sell', 'source', 'ratings', 'cocoa', 'top', 'bottom', 'barplot'],
                'companies':['country', 'region', 'ratings', 'cocoa', 'number_of_bars', 'top', 'bottom', 'barplot'],
                'countries':['region', 'sell', 'source', 'ratings', 'cocoa', 'number_of_bars', 'top', 'bottom', 'barplot'],
                'regions':['sell', 'source', 'ratings', 'cocoa', 'number_of_bars', 'top', 'bottom', 'barplot'],
                }
    valid = 1
    if response_split[0] in valid_op.keys():
        for idx, resp in enumerate(response_split):
            resp = resp.split('=')[0]
            if idx > 0:
                if resp not in valid_op[response_split[0]] and not resp.isnumeric():
                    valid = 0
    else:
        valid = 0
    return valid

def create_final_op(response):
    '''Update the default op command with user input to latest op command

    Parameters
    ----------
    response: string
        input command

    Returns
    -------
    list
        latest command with options in a list format
    '''
    response_split = response.split()
    op_list = [['bars', 'companies', 'countries', 'regions'],
               ['country', 'region'],
               ['sell', 'source'],
               ['ratings','cocoa','number_of_bars'],
               ['top','bottom']
              ]
    final_op = ['bars', 'none', 'sell', 'ratings', 'top', '10', '']
    for resp in response_split:
        input_op = resp.split('=')[0]
        for idx, op in enumerate(op_list):
            if input_op in op:
                final_op[idx] = input_op
                if idx == 1:
                    final_op[idx] = resp
        if input_op.isnumeric():
            final_op[-2] = input_op
        if input_op == 'barplot':
            final_op[-1] = 'barplot'
    return final_op

def create_final_query(final_op):
    '''Create the sql query syntax based on the latest op command

    Parameters
    ----------
    final_op: string list
        Latest input command after split into list

    Returns
    -------
    string
        put up together the final sql query syntax
    '''
    if final_op[0] == 'bars':
        q = '''
        SELECT SpecificBeanBarName, Company, sell.EnglishName, Rating, CocoaPercent, source.EnglishName
        FROM Bars, Countries source, Countries sell
        WHERE source.Alpha2="BR" AND Bars.BroadBeanOriginId=source.Id AND Bars.CompanyLocationId=sell.Id
        ORDER BY Rating ASC
        -- ORDER BY Rating DESC
        LIMIT 8
        '''
        if final_op[1] == 'none':
            q = q.replace('source.Alpha2="BR" AND ','')
        elif final_op[1].split('=')[0] == 'country':
            q = q.replace('source.Alpha2="BR"', f"{final_op[2]}.Alpha2='{final_op[1].split('=')[1]}'")
        elif final_op[1].split('=')[0] == 'region':
            q = q.replace('source.Alpha2="BR"', f"{final_op[2]}.Region='{final_op[1].split('=')[1]}'")
        map = {'ratings':'Rating', 'cocoa':'CocoaPercent', 'top':'DESC', 'bottom':'ASC'}
        q = q.replace('ORDER BY Rating ASC', f"ORDER BY {map[final_op[3]]} {map[final_op[4]]}")
        q = q.replace('LIMIT 8', f"LIMIT {final_op[5]}")

    if final_op[0] == 'companies':
        q = '''
        SELECT Company, EnglishName, COUNT(SpecificBeanBarName)
        FROM Bars
        JOIN Countries
                ON Bars.CompanyLocationId=Countries.Id
        -- 		ON Bars.BroadBeanOriginId=Countries.Id
        WHERE Region="Europe"
        GROUP BY Company
        HAVING COUNT(SpecificBeanBarName) > 4
        ORDER BY COUNT(SpecificBeanBarName) DESC
        LIMIT 8
        '''
        if final_op[1] == 'none':
            q = q.replace('WHERE Region="Europe"', '')
        elif final_op[1].split('=')[0] == 'country':
            q = q.replace('WHERE Region="Europe"', f"WHERE Alpha2='{final_op[1].split('=')[1]}'")
        elif final_op[1].split('=')[0] == 'region':
            q = q.replace('WHERE Region="Europe"', f"WHERE Region='{final_op[1].split('=')[1]}'")

        map = {'number_of_bars':'COUNT(SpecificBeanBarName)', 'ratings':'AVG(Rating)', 'cocoa':'AVG(CocoaPercent)', 'top':'DESC', 'bottom':'ASC'}
        q = q.replace('SELECT Company, EnglishName, COUNT(SpecificBeanBarName)', f"SELECT Company, EnglishName, {map[final_op[3]]}")
        q = q.replace('ORDER BY COUNT(SpecificBeanBarName) DESC', f"ORDER BY {map[final_op[3]]} {map[final_op[4]]}")
        q = q.replace('LIMIT 8', f"LIMIT {final_op[5]}")


    if final_op[0] == 'countries':
        q = '''
        SELECT EnglishName, Region, AVG(CocoaPercent)
        FROM Bars
            JOIN Countries
                ON Bars.CompanyLocationId=Countries.Id
        -- 		ON Bars.BroadBeanOriginId=Countries.Id
        WHERE Region="Asia"
        GROUP BY EnglishName
        HAVING COUNT(SpecificBeanBarName) > 4
        ORDER BY AVG(CocoaPercent) DESC
        LIMIT 8
        '''
        if final_op[1] == 'none':
            q = q.replace('WHERE Region="Asia"', '')
        elif final_op[1].split('=')[0] == 'region':
            q = q.replace('WHERE Region="Asia"', f"WHERE Region='{final_op[1].split('=')[1]}'")
        if final_op[2] == 'source':
            q = q.replace('ON Bars.CompanyLocationId=Countries.Id', 'ON Bars.BroadBeanOriginId=Countries.Id')
        map = {'number_of_bars':'COUNT(SpecificBeanBarName)', 'ratings':'AVG(Rating)', 'cocoa':'AVG(CocoaPercent)', 'top':'DESC', 'bottom':'ASC'}
        q = q.replace('SELECT EnglishName, Region, AVG(CocoaPercent)', f"SELECT EnglishName, Region, {map[final_op[3]]}")
        q = q.replace('ORDER BY AVG(CocoaPercent) DESC', f"ORDER BY {map[final_op[3]]} {map[final_op[4]]}")
        q = q.replace('LIMIT 8', f"LIMIT {final_op[5]}")

    if final_op[0] == 'regions':
        q = '''
        SELECT Region, AVG(Rating)
        FROM Bars
           JOIN Countries
         	    ON Bars.CompanyLocationId=Countries.Id
        --		ON Bars.BroadBeanOriginId=Countries.Id
        GROUP BY Region
        HAVING COUNT(SpecificBeanBarName) > 4
        ORDER BY AVG(Rating) DESC
        LIMIT 3
        '''
        if final_op[2] == 'source':
            q = q.replace('ON Bars.CompanyLocationId=Countries.Id', 'ON Bars.BroadBeanOriginId=Countries.Id')
        map = {'number_of_bars':'COUNT(SpecificBeanBarName)', 'ratings':'AVG(Rating)', 'cocoa':'AVG(CocoaPercent)', 'top':'DESC', 'bottom':'ASC'}
        q = q.replace('SELECT Region, AVG(Rating)', f"SELECT Region, {map[final_op[3]]}")
        q = q.replace('ORDER BY AVG(Rating) DESC', f"ORDER BY {map[final_op[3]]} {map[final_op[4]]}")
        q = q.replace('LIMIT 3', f"LIMIT {final_op[5]}")

    return q

def print_format(results, final_op):
    '''print result in an aligned format

    Parameters
    ----------
    results: list
        2-D array of result
    final_op: string list
        Latest input command after split into list

    Returns
    -------
    None
    '''
    results_format = []
    for row in results:
        col_format = []
        for idx,col in enumerate(row):
            if isinteger(col):
                col_format.append(col)
            elif isfloat(col):
                if idx ==4:
                    col_format.append("{:.2f}".format(col))
                else:
                    col_format.append("{:.1f}".format(col))
            else:
                if len(col)>12:
                    col_format.append(col[0:12] + '...')
                else:
                    col_format.append(col)
        results_format.append(col_format)

    # format for bars
    if final_op[0]=='bars':
        row_format = "{:<16}{:<16}{:<16}{:<5}{:<5.0%}{:<16}".format
        for row in results_format:
            print(row_format(row[0],row[1],row[2],row[3],float(row[4]),row[5]))

    # format for companies, countries
    elif final_op[0]=='companies' or final_op[0]=='countries':
        row_format = "{:<16}{:<16}{:<16}".format
        for row in results_format:
            print(row_format(row[0],row[1],row[2]))

    # format for regins
    elif final_op[0]=='regions':
        row_format = "{:<16}{:<16}".format
        for row in results_format:
            print(row_format(row[0],row[1]))
    print()

def plot_bar(results, final_op):
    '''barplot result

    Parameters
    ----------
    results: list
        2-D array of result
    final_op: string list
        Latest input command after split into list

    Returns
    -------
    None
    '''
    if final_op[-1] == 'barplot':
        x = []
        y = []
        if (final_op[0] == 'bars'):
            if final_op[3] == 'ratings':
                for row in results:
                    x.append(row[0])
                    y.append(row[3])
            elif final_op[3]  == 'cocoa':
                for row in results:
                    x.append(row[0])
                    y.append(row[4])
        if(final_op[0] == 'companies' or final_op[0] == 'countries'):
            for row in results:
                    x.append(row[0])
                    y.append(row[2])
        if(final_op[0] == 'regions'):
            for row in results:
                    x.append(row[0])
                    y.append(row[1])

        bar_data = go.Bar(x=x, y=y)
        basic_layout = go.Layout(title="Result")
        fig = go.Figure(data=bar_data, layout=basic_layout)
        # fig.show()
        fig.write_html("result.html", auto_open=True)

def isfloat(value):
    '''Check if value is float

    Parameters
    ----------
    value: value
        input value

    Returns
    -------
    Boolean
        is float or not
    '''
    try:
        float(value)
        return True
    except ValueError:
        return False

def isinteger(value):
    '''Check if value is integer

    Parameters
    ----------
    value: value
        input value

    Returns
    -------
    Boolean
        is integer or not
    '''
    return str(value).isnumeric()

# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":
    interactive_prompt()
    # response = 'bars country=BR source ratings bottom 8'
    # response = 'companies region=Europe number_of_bars 12'
    # response = 'countries region=Asia sell cocoa top'
    # response = 'regions source top 3'
    # response = 'bars ratings'
    # response = 'bars country=US sell cocoa bottom 5'
    # response = 'companies region=Europe number_of_bars'
    # response = 'companies ratings top 8'
    # response = 'countries number_of_bars'
    # response = 'countries region=Asia ratings'
    # response = 'regions number_of_bars'
    # response = 'regions ratings'
    # print(f'{text:>10} {number:3d}  {other_number:7.2f}')
