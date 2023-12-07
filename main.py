import os
import cloudscraper
import zipfile
import codecs
import pandas as pd
from bs4 import BeautifulSoup

outdir = "output/"

s = cloudscraper.create_scraper(disableCloudflareV1=True, browser="chrome", delay=10)

for _ in range(3):
    r = s.get("https://cbr.ru/s/newbik", allow_redirects=True)
    if r.status_code != 200:
        print(f"Error downloading zip: {r.status_code}")
        continue
    open("latest.zip", "wb").write(r.content)
    break

try:
    with zipfile.ZipFile("latest.zip", "r") as zr:
        zr.extractall(outdir)
        os.remove("latest.zip")
except Exception as e:
    print(f"Error unpacking file: {e}")
    exit(1)

for fp in os.listdir(outdir):
    if not fp.endswith("_full.xml"):
        continue
    with codecs.open(outdir + fp, "r", encoding="windows-1251") as f:
        content = f.read()
    s = BeautifulSoup(content, "lxml")

    data = []
    for entry in s.findAll("bicdirectoryentry"):
        row = entry.attrs
        for participant_info in entry.findAll("participantinfo"):
            row.update(participant_info.attrs)
        for swbic in entry.findAll("swbics"):
            row.update(swbic.attrs)
        for account in entry.findAll("accounts"):
            row.update(account.attrs)
        data.append(row)
    df = pd.DataFrame(data)

    df.to_csv(outdir + "latest.csv", index=False, header=True)
    df.to_csv(outdir + "latest.tsv", index=False, header=True, sep="\t", quoting=3)
    df.to_json(outdir + "latest.json", orient="records")
    df.to_xml(outdir + "latest.xml")
    os.remove(outdir + fp)
