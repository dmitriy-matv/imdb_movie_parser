import csv
import requests
from bs4 import BeautifulSoup

start_url = 'https://www.imdb.com/search/title/?genres=action&title_type=feature&explore=genres&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=facfbd0c-6f3d-4c05-9348-22eebd58852e&pf_rd_r=82MMWQ3AZRPC5SM46SG3&pf_rd_s=center-6&pf_rd_t=15051&pf_rd_i=genre&ref_=ft_gnr_mvpop_1'

class Movie_constructor:
    def __init__(self, title,year, certificate, runtime, genre, imdb_rating, metascope_rating, num_votes, director, stars, link):
        self.title = title
        self.year = year
        self.certificate = certificate
        self.runtime = runtime
        self.genre = genre
        self.imdb_rating = imdb_rating
        self.metascope_rating = metascope_rating
        self.num_votes = num_votes
        self.director = director
        self.stars = stars
        self.link = link


class IMDB_parser:
    def __init__(self, start_url):
        self.base_url = 'https://www.imdb.com'
        self.start_url = start_url
        self.session = self._init_session()
        self.movie_params = []
        self.movie_list = []
        self.next_link = ""
        self.current_page = ""


    def _init_session(self):
        with requests.Session() as se:
            se.headers = {
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
                "Accept": "text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8, application / signed - exchange;v = b3;q = 0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "uk - UA, uk;q = 0.9, ru;q = 0.8, en - US;q = 0.7, en;q = 0.6"
            }
            return se

    def set_next_link(self):
        try:
            self.next_link = self.base_url + (self.current_page.find("a", class_="lister-page-next next-page")['href'])
        except TypeError:
            self.next_link = None

    def get_start(self):
        resp = self.session.get(self.start_url)
        self.current_page = BeautifulSoup(resp.content, 'html.parser')
        self.set_next_link()

        self.collect_movies()

    def get_next_link(self):
        resp = self.session.get(self.next_link)
        self.current_page = BeautifulSoup(resp.content, 'html.parser')
        self.set_next_link()

        self.collect_movies()

    def collect_movies(self):
        for m in self.current_page.findAll("div", class_="lister-item mode-advanced"):
            self.movie_params.append(m.h3.contents[3].text.strip())  # Title
            self.movie_params.append(m.h3.contents[5].text.strip())  # Year
            try:
                self.movie_params.append(m.find("span", attrs={"class": "certificate"}).text.strip())  # certificate
            except:
                self.movie_params.append(0)
            try:
                self.movie_params.append(m.find("span", attrs={"class": "runtime"}).text.strip())  # runtime
            except:
                self.movie_params.append(0)
            try:
                self.movie_params.append(m.find("span", attrs={"class": "genre"}).text.strip())  # genre
            except:
                self.movie_params.append(0)
            try:
                self.movie_params.append(m.find("div",
                             attrs={"class": "inline-block ratings-imdb-rating"}).strong.text.strip())  # imdb rating
            except:
                self.movie_params.append(0)
            try:
                self.movie_params.append(m.find("div",
                             attrs={"class": "inline-block ratings-metascore"}).span.text.strip())  # metascore rating
            except:
                self.movie_params.append(0)
            try:
                self.movie_params.append(m.find("span", attrs={"name": "nv"}).text.strip())  # number of votes
            except:
                self.movie_params.append(0)
            try:
                self.movie_params.append(m.find("p", attrs={"class": ""}).text.split("|")[0].split(':')[1].strip())  # director(-s)
            except:
                self.movie_params.append(0)
            try:
                self.movie_params.append(m.find("p", attrs={"class": ""}).text.split("|")[1].split(':')[1].strip().replace('\n',""))  # Stars
            except:
                self.movie_params.append(0)
            try:
                self.movie_params.append(f"https://www.imdb.com{m.a.get('href')}") # link
            except:
                self.movie_params.append(0)

            movie = Movie_constructor(*self.movie_params)
            self.movie_params = []
            self.movie_list.append(movie)

    def write_movie_to_csv(self):
        f = open('movies.csv', 'w', encoding="utf-8")

        with f:
            writer = csv.writer(f)
            for movie in self.movie_list:
                writer.writerow(
                    [movie.title, movie.year, movie.certificate, movie.runtime, movie.genre, movie.imdb_rating,
                     movie.metascope_rating, movie.num_votes,
                     movie.director, movie.stars, movie.link])

    def get_movies_list_lenght(self):
        return len(self.movie_list)

    def get_all_movies(self):
        self.get_start()
        try:
            while self.next_link is not None:
                if len(self.movie_list) < 200000:
                    self.get_next_link()
                    print(f"Movies count => {len(self.movie_list)}")
                    print(self.next_link)
                else:
                    self.write_movie_to_csv()
                    return self.get_movies_list_lenght()
            self.write_movie_to_csv()
            return self.get_movies_list_lenght()
        except:
            self.write_movie_to_csv()
            return self.get_movies_list_lenght()


if __name__ == "__main__":

    imp = IMDB_parser(start_url)

    print(imp.get_all_movies())
