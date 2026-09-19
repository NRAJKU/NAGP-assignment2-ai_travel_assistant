from pathlib import Path
import json, re, requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"data"/"raw"; REG=ROOT/"data"/"source_registry.json"

def clean_html(html):
    soup=BeautifulSoup(html,"html.parser")
    for tag in soup(["script","style","noscript","svg"]): tag.decompose()
    lines=[x.strip() for x in soup.get_text("\n").splitlines() if x.strip()]
    return "\n".join(lines)

for item in json.loads(REG.read_text(encoding="utf-8")):
    slug=re.sub(r"[^a-z0-9]+","_",item["title"].lower()).strip("_")[:70]
    try:
        r=requests.get(item["url"],headers={"User-Agent":"AI-Travel-Planning-Assistant-Educational/1.0"},timeout=30)
        r.raise_for_status()
        text=f"# {item['title']}\nsource_url: {item['url']}\nsource_type: {item['type']}\n\n{clean_html(r.text)}\n"
        (OUT/f"fetched_{slug}.md").write_text(text,encoding="utf-8")
        print("Fetched",item["title"])
    except Exception as exc:
        print("WARNING:",item["title"],exc)
print("Review fetched files for reuse/licensing before redistributing them. The included curated notes remain the reproducible knowledge base.")
