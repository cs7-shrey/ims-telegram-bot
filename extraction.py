import os
import re
import requests
from bs4 import BeautifulSoup
import mysql.connector

mydb = mysql.connector.connect(
    host = os.getenv('MYSQLHOST'),
    user = os.getenv('MYSQLUSER'),
    password = os.getenv('MYSQLPASSWORD'),
    database = os.getenv('MYSQLDATABASE'),
    port=os.getenv('MYSQLPORT')
)
cursor = mydb.cursor()


# algorithm for pushing new notices
def find_new_notices(new_capture: list, old_capture: list):
    new_notices = []
    n: int = len(new_capture)
    i: int = 0
    j: int = 0
    quit: bool = False
    for x in range(n):
        for y in range(n):
            if old_capture[x] == new_capture[y]:
                i = x
                j = y
                quit = True
                break
        if quit:
            break
    if i == 0 and j == 0:
        return new_notices
    elif j == 0 and i > j:
        return new_notices
    elif j != 0:
        j -= 1
        while(j >= 0):
            new_notices.append(new_capture[j])
            j -= 1
        return new_notices


def get_old_state():
    cursor.execute("SELECT content FROM notices")
    results = cursor.fetchall()
    old_state = [i[0] for i in results]
    old_state = [i.strip() for i in old_state]
    return old_state

def get_new_soup():
    url = "https://www.imsnsit.org/imsnsit/notifications.php"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    pattern = r'^\d{2}-\d{2}-\d{4}$'
    regex = re.compile(pattern)
    
    # fonts = soup.find_all('font')
    all_tds = soup.find_all('td')[6:156]
    new_soup = []
    for td in all_tds:
        if td.find('hr') or regex.match(td.find('font').text.strip()):
            continue
        new_soup.append(td)
    return new_soup

def get_new_state(new_soup):
    new_state = [td.text.split('Published')[0] for td in new_soup]
    return new_state

# a random comment
def extract_and_update():
    old_state = get_old_state()
    new_soup = get_new_soup()
    new_state = get_new_state(new_soup=new_soup)
    print(old_state[0], new_state[0])
    new_notices = find_new_notices(new_state, old_state)
    print(new_notices)

    count = 0
    if new_notices:
        list1 = ["(%s, %s)"] * 50
        placeholders = ", ".join(list1)
        notice_ids = tuple(range(50))
        tuple_notices = tuple(new_state)
        temp_list = []
        for i in range(50):
            temp_list.append(notice_ids[i])
            temp_list.append(new_state[i])
        data = tuple(temp_list)
        # deleting previous notices    
        cursor.execute("DELETE FROM notices")
        mydb.commit()
        # adding the new state of notices
        cursor.execute(f"INSERT INTO notices (id, content) VALUES {placeholders}", data)
        mydb.commit()

        # checking for notices with file content
        to_check = new_soup[:len(new_notices)]
        for td in to_check:
            if td.find('a'):
                count += 1;
    notice_info = {"notices": new_notices, "n_files": count}
    return notice_info

def main():
    ...

if __name__ == "__main__":
    main() 