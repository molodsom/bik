import os
import cloudscraper
import zipfile
import codecs
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

urlpath = "https://cbr.ru/vfs/mcirabis/BIKNew/"
filename = datetime.now().strftime('%Y%m%d') + "ED01OSBR.zip"
outdir = "output/"
outzip = outdir + filename

s = cloudscraper.create_scraper(disableCloudflareV1=True, browser="chrome", delay=10)

for _ in range(3):
    r = s.get(urlpath + filename, allow_redirects=True)
    if r.status_code != 200:
        print(f"Error downloading zip: {r.status_code}")
        continue
    open(outzip, "wb").write(r.content)
    break

try:
    with zipfile.ZipFile(outzip, 'r') as zr:
        zr.extractall(outdir)
        os.remove(outzip)
except Exception as e:
    print(f"Error unpacking file: {e}")
    exit(1)

for fp in os.listdir(outdir):
    if not fp.endswith("_full.xml"):
        continue
    with codecs.open(outdir + fp, "r", encoding="windows-1251") as f:
        content = f.read()
    s = BeautifulSoup(content, "lxml")
    df = pd.DataFrame(data=[r.attrs for r in s.findAll("participantinfo")])
    df.to_csv(outdir + "latest.csv", index=False, header=True)
    df.to_csv(outdir + "latest.tsv", index=False, header=True, sep="\t", quoting=3)
    df.to_json(outdir + "latest.json", orient="records")
    df.to_xml(outdir + "latest.xml")
    os.remove(outdir + fp)
