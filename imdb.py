from typing import NamedTuple, List, Set
from pyquery import PyQuery as pq
import json
from datetime import datetime


class Movie(NamedTuple):
    url: str
    title: str
    description: str
    released: datetime
    poster_url: str
    genre: str
    audience_rating: str
    actors: List[str]
    director: List[str]
    creators: List[str]
    rating: float
    review: str
    images: Set[str]

    @property
    def years_old(self) -> int:
        return int((datetime.now() - self.released).days / 365)


def as_list(obj: dict, field: str) -> List:
    data = obj.get(field, [])
    if data is None:
        return []
    if isinstance(data, list):
        return data
    return [data]


def parse_movie(content: str) -> Movie:
    root = pq(content)
    url = root.find('meta[property="og:url"]').attr("content")
    title = root.find('meta[property="og:title"]').attr("content")

    meta_data = json.loads(root.find('script[type="application/ld+json"]').text())
    released = datetime.strptime(meta_data['datePublished'], '%Y-%m-%d')
    images = set()
    for img in root.find('img.loadlate'):
        images.add(pq(img).attr('loadlate'))
    return Movie(url=url,
                 title=title,
                 released=released,
                 description=meta_data['description'],
                 poster_url=meta_data['image'],
                 genre=meta_data['genre'],
                 audience_rating=meta_data['contentRating'],
                 actors=[x['name'] for x in as_list(meta_data, 'actor') if 'name' in x],
                 director=[x['name'] for x in as_list(meta_data, 'director') if 'name' in x],
                 creators=[x['name'] for x in as_list(meta_data, 'creator') if 'name' in x],
                 rating=float(meta_data['aggregateRating']['ratingValue']),
                 review=meta_data.get('review', {'reviewBody': ''})['reviewBody'],
                 images=images,
                 )


if __name__ == '__main__':
    with open('sample.html', 'rt') as f:
        content = f.read()
    movie = parse_movie(content)
