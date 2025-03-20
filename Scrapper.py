from bs4 import BeautifulSoup
import requests
from SubjectInfo import Subject

def check_num(value: str):
    try:
        num = int(value)
    except ValueError:
        return False
    return True

def paper_code_parser(paper_code_list: list):
    variant_list = []
    paper_number = []
    for paper_code in paper_code_list:
        paper_code = paper_code.text
        paper_code = paper_code.translate({ ord(i): " " for i in '_.'})
        split_paper_code = paper_code.split()
        if len(split_paper_code) == 5 and check_num(split_paper_code[3]) is True:
            variant_number = str(split_paper_code[3])
            if int(variant_number[0]) not in paper_number:
                paper_number.append(int(variant_number[0]))
            if int(variant_number[-1]) not in variant_list:
                variant_list.append(int(variant_number[-1]))
    paper_number.sort()
    variant_list.sort()
    return paper_number, variant_list
            

def subject_list_parser(div_text_list: list[str]):
    subjects = {}
    for div_text in div_text_list:
        subject_url = div_text.replace(" ", "-")
        subject_url = f"{subject_url.lower()}/"
        split_div_text = div_text.split()
        subject_code = (split_div_text[-1]).translate({ ord(i): None for i in '()'})
        split_div_text.pop(-1)
        subject_name = ""
        for i, text in enumerate(split_div_text):
            text = text.translate({ord(i): None for i in '()'})
            text = text.replace(" ", "")
            if text == "-":
                pass
            elif (text not in ["AS","Level","only","A","for","final","examination","in","first",]
                and check_num(text) is not True):
                subject_name = f"{subject_name} {text}"
        subjects[subject_code] = Subject(subject_name, subject_code, subject_url)
    return subjects

def load_page(url):
    page = requests.get(url)
    html = page.text
    soup = BeautifulSoup(html, "lxml")
    soup.prettify()
    return soup

class Fetcher:
    def __init__(self, board: str) -> None:
        self.root_url = "https://papers.gceguide.cc/"
        self.board = board
        self.url_substitute = {"A levels": "a-levels/", "O levels": "o-levels/", "IGCSE": "cambridge-IGCSE/"}
        self.define_url()
        self.initializer()
        
    def initializer(self):
        self.fetch_subject_list()
        
    def define_url(self):
        self.main_url = self.root_url + self.url_substitute[self.board]
    
    def fetch_subject_list(self):
        soup = load_page(self.main_url)
        html_subjects_list = soup.find_all("li", class_=['dir'])
        subject_list_unparsed = [val.text for val in html_subjects_list] # type: ignore
        self.subjects = subject_list_parser(subject_list_unparsed)
        return self.subjects
    
    def fetch_paper_range(self, code: str):
        advanced_url = f"{self.main_url}{(self.subjects[code]).url_extension}"
        (self.subjects[code]).url_link = advanced_url
        soup = load_page(advanced_url)
        year_a_tags = soup.find_all("a", class_=['name'])
        for year_a_tag in year_a_tags:
            year = year_a_tag.get("href")
            if check_num(year) is True:
                (self.subjects[code]).year_range.append(int(year))
        return (False, self.subjects) if len(self.subjects[code].year_range) == 0 else (True, self.subjects)
    
    def fetch_paper_info(self, code: str):
        if len(self.subjects[code].year_range) > 0:
            internal_url = f"{(self.subjects[code].url_link)}{self.subjects[code].year_range[-1]}/"
        else:
            internal_url = self.subjects[code].url_link
        soup = load_page(internal_url)
        paper_html_link_list = soup.find_all("a", class_=['name'])
        self.subjects[code].papers, self.subjects[code].variants = paper_code_parser(paper_html_link_list)
        return self.subjects


