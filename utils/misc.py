import aiohttp
import bs4 as bs4


def split_str(string, split_at=2000):
    splitted = []
    if string:
        splitted = [string[i:i + split_at] for i in range(0, len(string), split_at)]
    return splitted


def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])
    return content.strip('` \n')


def get_syntax_error(e):
    if e.text is None:
        return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
    return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)


async def get_lyrics(query, token):
    # Shit doesnt work
    url = "http://api.genius.com/search"
    params = {"q": query, "page": 1}
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            results = data["response"]["hits"]

        if len(results) < 1:
            return {"error": f"No results found for \"{query}\""}

        result = results[0]["result"]
        response = await session.get(result["url"])
        bs = bs4.BeautifulSoup(await response.read(), "html.parser")

    # Remove script tags from the lyrics
    for script_tag in bs.find_all("script"):
        script_tag.extract()

    lyrics = bs.find("lyrics").get_text()

    return {
        "title": result["title"],
        "url": result["url"],
        "path": result["path"],
        "thumbnail": result.get("thumbnail"),
        "header_image_url": result["song_art_image_thumbnail_url"],
        "primary_artist": result["primary_artist"],
        "lyrics": lyrics
    }

