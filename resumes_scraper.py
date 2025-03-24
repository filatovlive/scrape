
#!/usr/bin/python

import codecs
from bs4 import BeautifulSoup
from json import dumps
import requests
from datetime import datetime
import os.path
import pandas as pd

listArticle = []

def praseOne(cookies, element, sector):
    d = dict()
    linkA = "https://www.work.ua" + str(element.h2.a["href"])
    uuid = str(element.a["href"])
    
    # Avoid adding duplicates based on 'uuid'
    if any(article.get("uuid") == uuid for article in listArticle):
        print(f"Duplicate found, skipping: {uuid}")
        return
    
    try:
        d["uuid"] = uuid
        d["link"] = str(linkA)
        d["sector"] = sector  # Add sector value to the dictionary
        
        page = requests.get(linkA,
                            cookies={'required_cookie': cookies},
                            headers={'User-Agent': 'Mozilla/5.0'}).text
        
        soup = BeautifulSoup(page, 'html.parser')
        title = soup.find('h1')
        if title is not None:
            d["title"] = title.get_text(strip=True)
        
        position = soup.h2.get_text(strip=True) if soup.h2 else None
        if position is not None:
            d["profession"] = position
        
        salary_element = soup.find("h2").find("span")
        if salary_element is not None:
            salary = salary_element.text.strip()
            d["salary"] = salary[2:]
        
        contractType = soup.find('dt', string='Employment:')
        if contractType is not None:
            dd = contractType.find_next_sibling('dd')
            if dd:
                d["contract_type"] = dd.text.strip()

        ageType = soup.find('dt', string='Age:')
        if ageType is not None:
            dd = ageType.find_next_sibling('dd')
            if dd:
                d["age"] = dd.text.strip()
        
        residenceType = soup.find('dt', string=lambda text: text and 'City' in text)
        if residenceType is not None:
            dd = residenceType.find_next_sibling('dd')
            if dd:
                d["residence"] = dd.text.strip()

        workType = soup.find('dt', string='Ready to work:')
        if workType is not None:
            dd = workType.find_next_sibling('dd')
            if dd:
                d["ready_to_work"] = dd.text.strip()

        educationType = soup.find('h2', string='Education')
        if educationType is not None:
            d["education"] = educationType.find_next_sibling('p').text.strip()

        skillsType = soup.find('div', class_='flex flex-wrap')
        if skillsType is not None:
            skills = [span.text for span in skillsType.find_all('span')]
            d["skills"] = ''.join(skills)

        languageType = soup.find('h2', string='Language proficiencies')
        if languageType is not None:
            next_element = languageType.find_next_sibling()
            d["languages"] = next_element.get_text()

        disabilityType = soup.find('h2', string='Disability')
        if disabilityType is not None:
            next_element = disabilityType.find_next_sibling()
            d["disability"] = next_element.get_text()
        
        listArticle.append(d)
    except requests.RequestException as e:
        print(f"Error fetching details for {linkA}: {e}")
        # Handle errors if necessary

print("Fetching started:", datetime.now())
cookies = 'wdid=01HA9H9GWFZ9AKASZ78SMPBY2P; wsid=01HA9H9GWFZ9AKASZ78SMPBY2N'

links = [["https://www.work.ua/en/resumes-kh-accounting/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-administration/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-agriculture/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-transport/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-banking-finance/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-beauty-sports/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-construction-architecture/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-culture-music-showbiz/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-customer-service/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-design-art/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-education-scientific/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-healthcare/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-hotel-restaurant-tourism/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-hr-recruitment/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-insurance/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-it/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-legal/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-supply-chain/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-management-executive/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-marketing-advertising-pr/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-office-secretarial/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-production-engineering/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-publishing-media/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-real-estate/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-retail/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-sales/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-security/?gender=87&period=3",
"https://www.work.ua/en/resumes-kh-telecommunications/?gender=87&period=3"]
]

for link in links:
    initial_page = requests.get(link,
                                cookies={'required_cookie': cookies},
                                headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(initial_page, "html.parser")
    
    # Extract the total page count by finding all numbered page links
    pagination = soup.find('ul', class_='pagination hidden-xs')
    if pagination:
        page_numbers = [int(a.get_text(strip=True)) for a in pagination.find_all('a') if a.get_text(strip=True).isdigit()]
        r = max(page_numbers) if page_numbers else 1  # Use the maximum page number found, or default to 1
    else:
        r = 1

    sector = link.split('/')[-2][11:]  # Extract sector from the link

    for i in range(1, r + 1):
        pagelink = f"{link}&page={i}"
        print("Processing Page", i, "out of", r)
        try:
            page = requests.get(pagelink,
                                cookies={'required_cookie': cookies},
                                headers={'User-Agent': 'Mozilla/5.0'}).text
            soup = BeautifulSoup(page, 'html.parser')
            for p in soup.find_all('div', {'class': 'resume-link'}):
                praseOne(cookies, p, sector)  # Pass the sector to praseOne function
        except requests.RequestException as e:
            print(f"Error fetching page {pagelink}: {e}")

path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))).replace('\\', '/')

filePathXLSX = f"{path}/output/xlsx/job_scraper{datetime.today().strftime('%d_%m_%Y')}.xlsx"
if os.path.isfile(filePathXLSX):
    i = 2
    filePathXLSX = f"{path}/output/xlsx/job_scraper{datetime.today().strftime('%d_%m_%Y')}_v{str(i)}.xlsx"
    while os.path.isfile(filePathXLSX):
        i += 1
        filePathXLSX = f"{path}/output/xlsx/job_scraper{datetime.today().strftime('%d_%m_%Y')}_v{str(i)}.xlsx"

filePathJSON = f"{path}/output/json/job_scraper{datetime.today().strftime('%d_%m_%Y')}.json"
if os.path.isfile(filePathJSON):
    i = 2
    filePathJSON = f"{path}/output/json/job_scraper{datetime.today().strftime('%d_%m_%Y')}_v{str(i)}.json"
    while os.path.isfile(filePathJSON):
        i += 1
        filePathJSON = f"{path}/output/json/job_scraper{datetime.today().strftime('%d_%m_%Y')}_v{str(i)}.json"

with codecs.open(filePathJSON.replace('/src', ''), 'w', "utf-8") as f:
    f.write(dumps(listArticle, indent=2, ensure_ascii=False))

df = pd.DataFrame.from_dict(listArticle)
df.to_excel(filePathXLSX.replace('/src', ''), index=False)
