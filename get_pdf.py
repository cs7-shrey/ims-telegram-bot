from bs4 import BeautifulSoup
import io
import re
import requests


headers = {
    "Host": "www.imsnsit.org",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,en-IN;q=0.8",
    "Connection": "keep-alive",
    "Cookie": "PHPSESSID=02gli13eqrolbpgi2qgp2qlad1",
    "sec-ch-ua-platform": "Windows",
    "Referer": "https://www.imsnsit.org/imsnsit/notifications.php"
}

def get_hrefs(top_n: int):
    url = "https://www.imsnsit.org/imsnsit/notifications.php"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    a_tags = soup.find_all('a', title='NOTICES / CIRCULARS')
    hrefs = [a.get('href') for a in a_tags]
    return hrefs[:top_n]

def is_pattern(filename):
    pattern1 = re.compile(r'\.pdf$', re.IGNORECASE)
    pattern2 = re.compile(r'\.docx$', re.IGNORECASE)
    pattern3 = re.compile(r'\.jpg$', re.IGNORECASE)
    pattern4 = re.compile(r'\.png$', re.IGNORECASE)
    pattern5 = re.compile(r'\.jpeg$', re.IGNORECASE)

    return pattern1.search(filename) or pattern2.search(filename) or pattern3.search(filename)
def get_pdf_file(href: str):
    # Regex pattern to match strings that start with the specified URL
    # pattern = r"^https://www\.imsnsit\.org/imsnsit/plum_url\.php"
    response = requests.get(href, headers=headers)
    pdf_file = io.BytesIO(response.content)
    filename = response.headers.get('Content-Disposition').split('"')[1]
    pattern1 = re.compile(r'\.pdf$', re.IGNORECASE)
    pattern2 = re.compile(r'\.docx$', re.IGNORECASE)
    pattern3 = re.compile(r'\.jpg$', re.IGNORECASE)
    filename = filename if is_pattern(filename) else filename + '.pdf'
    return {"pdf": pdf_file, "filename": filename}


