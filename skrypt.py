import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import os
import time

# Scraping danych influencerów
URL = 'https://en.wikipedia.org/wiki/List_of_most-followed_TikTok_accounts'
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table', {'class': 'wikitable'})
rows = table.find_all('tr')[1:11]

influencers = []
for row in rows:
    cols = row.find_all(['td', 'th'])
    rank = cols[0].text.strip()
    name = cols[2].text.strip() # nieużywane
    username = cols[1].text.strip()
    followers = cols[4].text.strip()
    likes = cols[5].text.strip()
    description = cols[6].text.strip()
    country = cols[7].text.strip()

    slug = username.replace('@', '').replace('.', '').replace(' ', '-').lower()

    influencers.append({
        'rank': rank,
        'name': name,
        'username': username,
        'followers': followers,
        'likes': likes,
        'description': description,
        'country': country,
        'slug': slug
    })

# Tworzenie katalogu na zdjęcia
os.makedirs('assets/influencers', exist_ok=True)

# Pobieranie zdjęć za pomocą DuckDuckGo
with DDGS() as ddgs:
    for influencer in influencers:
        query = f"{influencer['name']} TikTok"
        print(f"Pobieram zdjęcie dla: {influencer['name']}")
        results = list(ddgs.images(query, max_results=1))
        
        if results:
            img_url = results[0]['image']
            img_data = requests.get(img_url).content
            img_filename = f"assets/influencers/{influencer['slug']}.jpg"
            
            with open(img_filename, 'wb') as img_file:
                img_file.write(requests.get(results[0]['image']).content)
            
            influencer['img_path'] = f"/assets/influencers/{influencer['slug']}.jpg"
        else:
            influencer['img_path'] = None

        time.sleep(5)  # unikaj blokady DuckDuckGo

# Generowanie strony Markdown (głównej)
with open('_posts/2025-03-09-influencers.md', 'w', encoding='utf-8') as main_file:
    main_file.write('---\nlayout: post\ntitle: "Top 10 influencerów TikToka"\ndate: 2025-03-09\ncategories: tiktok\n---\n\n')

    i = 1
    for influencer in influencers:
        main_file.write(f"## {i} [{influencer['name']}](/influencers/{influencer['slug']}/)\n")
        i += 1

# Generowanie podstron influencerów
os.makedirs('influencers', exist_ok=True)

for influencer in influencers:
    filename = f"influencers/{influencer['slug']}.md"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write('---\n')
        file.write('layout: page\n')
        file.write(f"title: \"{influencer['name']} ({influencer['username']})\"\n")
        file.write(f"permalink: /influencers/{influencer['slug']}/\n")
        file.write('---\n\n')

        if 'img_path' in influencer:
            file.write(f"![{influencer['name']}]({influencer['img_path']})\n\n")

        file.write(f"- **Ranking:** {influencer['rank']}\n")
        file.write(f"- **Obserwujący:** {influencer['followers']}\n")
        file.write(f"- **Polubienia (w bilionach:)** {influencer['likes']}\n")
        file.write(f"- **Kraj:** {influencer['country']}\n\n")
        file.write(f"- **Opis:** {influencer['description']}\n\n")

        file.write(f"[Więcej zdjęć w Google Images](https://www.google.com/search?tbm=isch&q={influencer['name'].replace(' ', '+')}+TikTok)\n\n")

        time.sleep(5)  # dłuższe pauzy, aby uniknąć limitów

print("gotowe!")
