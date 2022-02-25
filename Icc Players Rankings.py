import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    }

urls = [
"https://www.icc-cricket.com/rankings/mens/player-rankings/test/batting",
"https://www.icc-cricket.com/rankings/mens/player-rankings/test/bowling",
"https://www.icc-cricket.com/rankings/mens/player-rankings/odi/batting",
"https://www.icc-cricket.com/rankings/mens/player-rankings/odi/bowling",
"https://www.icc-cricket.com/rankings/mens/player-rankings/t20i/batting",
"https://www.icc-cricket.com/rankings/mens/player-rankings/t20i/bowling"
]

results = "All Ranking List.csv"
final_columns = ["Ranking Type", "Position", "Player Name", "Team Name", "Rating", "Career Best Rating"]
pd.DataFrame(columns=final_columns).to_csv(results, sep="\t", index=False, encoding="utf-8")

for url in urls:
    request = requests.get(url, headers=headers)
    content = request.text
    print(request.status_code, "->", url)
    soup = BeautifulSoup(content, "lxml")
    for element in soup.select('[class="ranking-pos up"], [class="ranking-pos down"]'):
        element.replace_with(BeautifulSoup("<" + element.name + "></" + element.name + ">", "html.parser"))

    ranking = soup.select_one(".rankings-block__title-container > h4").text

    result = ranking + ".csv"
    column_names = ["Position", "Player Name", "Team Name", "Rating", "Career Best Rating", "Crawl URL"]
    pd.DataFrame(columns=column_names).to_csv(result, sep="\t", index=False, encoding="utf-8")

    for element in soup.select('table[class="table rankings-table"] tr'):
        if(element.find("th")):
            continue
        data = dict()
        data["Ranking Type"] = ranking
        if(element.select_one('[class*="position"]')):
            data["Position"] = element.select_one('[class*="position"]').text
        for player_name in (element.select('a[href*="/player-rankings"]')):
            if(player_name.text.strip()):
                data["Player Name"] = player_name.text
        if(element.select_one('[class^="flag-15"]')):
            data["Team Name"] = element.select_one('[class^="flag-15"]')["class"][-1]
        if(element.select_one('[class$="rating"]')):
            data["Rating"] = element.select_one('[class$="rating"]').text
        if(element.select_one('td.u-hide-phablet')):
            data["Career Best Rating"] = element.select_one('td.u-hide-phablet').text
        for key in data.keys():
            data[key] = re.sub(r"\s+", " ", data[key])
            data[key] = data[key].strip()
        pd.DataFrame([data], columns=column_names).to_csv(result, sep="\t", index=False, header=False, encoding="utf-8", mode="a")
        pd.DataFrame([data], columns=final_columns).to_csv(results, sep="\t", index=False, header=False, encoding="utf-8", mode="a")