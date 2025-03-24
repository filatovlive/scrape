import os
import re
import codecs
import requests
import pandas as pd
from bs4 import BeautifulSoup
from json import dumps
from urllib.error import URLError
from datetime import datetime

listArticle = []

def parse_one(element):
    d = dict()
    linkA = "https://www.work.ua" + str(element.h2.a["href"])
    try:
        d["uuid"] = str(element.a["href"])
        d["link"] = linkA

        page = requests.get(linkA, headers={'User-Agent': 'Mozilla/5.0'}).text
        soup = BeautifulSoup(page, 'html.parser')

        # Title
        title = soup.find('h1', attrs={'id': 'h1-name'})
        d["title"] = title.get_text(strip=True) if title else "Not specified"

        # Salary
        salary = soup.select_one("li.text-indent.no-style.mt-sm.mb-0 span.strong-500")
        d["salary"] = salary.get_text(strip=True) if salary and "UAH" in salary.get_text() else "Not specified"

        # Company
        jobsCompany = soup.select_one("div.sm\\:mr-sm.flex-1 a")
        d["company"] = jobsCompany.get_text(strip=True) if jobsCompany else "Not specified"

        # Sector
        sector = soup.select_one("div.sm\\:mr-sm.flex-1 p.mt-sm.mb-0")
        d["sector"] = sector.get_text(strip=True).split(",")[0] if sector else "Not specified"

        # Location
        location = soup.select_one("li.text-indent.no-style.mt-sm.mb-0 span.glyphicon-map-marker")
        d["location"] = location.parent.get_text(strip=True) if location else "Not specified"

        # Employee
        employee = soup.select_one("li.text-indent.no-style.mt-sm.mb-0 span.nowrap")
        d["employee"] = employee.get_text(strip=True) if employee else "Not specified"

        # Contact info
        contact_name = soup.select_one("li.text-indent.no-style.mt-sm.mb-0 span.mr-sm")
        contact_phone = soup.select_one("span#contact-phone")
        d["contact name"] = contact_name.get_text(strip=True) if contact_name else "Not specified"
        if contact_phone:
            phone_text = contact_phone.get_text(strip=True)
            d["contact phone"] = re.search(r'\+?\d{9,}', phone_text).group() if re.search(r'\+?\d{9,}', phone_text) else "Not specified"
        else:
            d["contact phone"] = "Not specified"

        # Contract type
        contractType = soup.select_one("li.text-indent.no-style.mt-sm.mb-0 span.glyphicon-tick")
        d["contract"] = contractType.parent.get_text(strip=True) if contractType else "Not specified"

        # Job description
        jobDesc = soup.find('div', attrs={'id': 'job-description'})
        d["job description"] = jobDesc.get_text(strip=True) if jobDesc else "Not specified"

    except URLError:
        print(f"⚠️ Error fetching: {linkA}")
        fields = ["title", "salary", "company", "sector", "employee", "location",
                  "contact name", "contact phone", "contract", "job description"]
        for field in fields:
            d[field] = "error"

    listArticle.append(d)


# ================================
# Pagination + Job List Scraping
# ================================
links = ["https://www.work.ua/en/jobs-nk/?page="]
for link in links:
    first_page = requests.get(link + "1", headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(first_page, "html.parser")

    pagination = soup.find('ul', class_='pagination hidden-xs')
    total_pages = 1

    if pagination:
        try:
            page_el = pagination.select_one("li:nth-child(6) a")
            total_pages = int(page_el.get_text(strip=True)) if page_el else 1
        except Exception:
            print("⚠️ Could not determine page count. Defaulting to 1.")

    for i in range(1, total_pages + 1):
        print(f"📄 Processing Page {i} of {total_pages}")
        try:
            pagelink = link + str(i)
            page = requests.get(pagelink, headers={'User-Agent': 'Mozilla/5.0'}).text
            soup = BeautifulSoup(page, 'html.parser')
            for p in soup.find_all('div', {'class': 'job-link'}):
                parse_one(p)

        except URLError:
            print(f"⚠️ Failed to load page: {pagelink}")


# ================================
# Saving JSON and Excel
# ================================
base_path = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')
date_str = datetime.today().strftime('%d_%m_%Y')

# JSON output
json_dir = f"{base_path}/output/json"
os.makedirs(json_dir, exist_ok=True)
json_path = f"{json_dir}/job_scraper{date_str}.json"
i = 2
while os.path.isfile(json_path):
    json_path = f"{json_dir}/job_scraper{date_str}_v{i}.json"
    i += 1

with codecs.open(json_path, 'w', "utf-8") as f:
    f.write(dumps(listArticle, indent=2, ensure_ascii=False))

# Excel output
xlsx_dir = f"{base_path}/output/xlsx"
os.makedirs(xlsx_dir, exist_ok=True)
xlsx_path = f"{xlsx_dir}/job_scraper{date_str}.xlsx"
i = 2
while os.path.isfile(xlsx_path):
    xlsx_path = f"{xlsx_dir}/job_scraper{date_str}_v{i}.xlsx"
    i += 1

df = pd.DataFrame.from_dict(listArticle)
df.to_excel(xlsx_path, index=False)

print("✅ Scraping complete.")
print(f"📁 JSON saved to: {json_path}")
print(f"📁 Excel saved to: {xlsx_path}")
