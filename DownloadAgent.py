from SubjectInfo import Subject
import os
import shutil
import asyncio
import aiohttp
from aiohttp.client import ClientSession
import aiofiles

class Filer:
    def __init__(self, folder_name) -> None:
        self.folder_name = folder_name
        self.root_directory = None
        self.downloads_folder_path = None
        self.main_directory = None
        self.setup_filing()
    
    def setup_filing(self):
        self.root_directory = os.getcwd()
        self.downloads_folder_path = f"{self.root_directory}\\Downloads"
        if os.path.isdir(self.downloads_folder_path) is False:
            os.mkdir(self.downloads_folder_path)
    
    def initialize(self, year: str):   
        self.main_directory = f"{self.downloads_folder_path}\\{self.folder_name}"
        if os.path.isdir(self.main_directory) is not False:
            shutil.rmtree(self.main_directory)
        os.mkdir(self.main_directory)
    
    def update(self, year: str):
        self.current_directory = f"{self.main_directory}\\{year}"
        os.mkdir(self.current_directory)
    
    def make_internal_directory(self, month):
        self.current_month_directory = f"{self.current_directory}\\{month}"
        os.mkdir(self.current_month_directory)
        return self.current_month_directory
    
    def delete_directory(self, directory_type: str):
        if directory_type == "internal":
            contents = os.listdir(self.current_month_directory)
            if len(contents) == 0:
                shutil.rmtree(self.current_month_directory)
        elif directory_type == "current":
            contents = os.listdir(self.current_directory)
            if len(contents) == 0:
                shutil.rmtree(self.current_directory)

    
async def download_link(url:str,path , session:ClientSession):
    async with session.get(url, allow_redirects=True) as res:
        if res.ok:
            f = await aiofiles.open(path, mode='wb')
            await f.write(await res.read())
            await f.close()

async def download_all(urls:dict):
    my_conn = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(download_link(url=url,path=urls[url],session=session))
            tasks.append(task)
        await asyncio.gather(*tasks,return_exceptions=True)

class DownloadAgent:
    def __init__(self, range: tuple[int, int], variants: list[int], papers: list[int], subject_code: str, subject: Subject) -> None:
        self.range = range
        self.variants = variants
        self.papers = papers
        self.subject_code = subject_code
        self.subject = subject
        self.seasons = {"February-March": "m", "May-June" : "s", "October-November": "w"}


    def initialize(self):
        folder_name = f"{self.subject.name} ({self.subject.code})"
        self.session = Filer(folder_name)
        self.session.initialize(str(self.range[0]))
        return (
            len(list(iter(self.subject.variants and self.variants))) > 0
            and len(list(iter(self.subject.papers and self.papers))) > 0
            and len(list(iter(self.subject.year_range and self.range))) > 0
        )
        
    def download_papers(self):
        year = self.range[0]
        while year <= self.range[-1]:
            self.session.update(str(year))
            main_url = f"{self.subject.url_link}{year}/"
            for season in self.seasons.keys():
                path = self.session.make_internal_directory(season)
                season_url = f"{self.seasons[season]}{str(year)[-2]}{str(year)[-1]}"
                link_dict = {}
                for paper in self.papers:
                    for variant in self.variants:
                        qp = f"{main_url}{self.subject_code}_{season_url}_qp_{paper}{variant}.pdf"
                        ms = f"{main_url}{self.subject_code}_{season_url}_ms_{paper}{variant}.pdf"
                        qp_path = f"{path}\\QP-paper({paper})variant({variant}).pdf"
                        ms_path = f"{path}\\MS-paper({paper})variant({variant}).pdf"
                        link_dict[qp] = qp_path
                        link_dict[ms] = ms_path
                asyncio.run(download_all(link_dict))
                self.session.delete_directory("internal")
            self.session.delete_directory("current")
            year += 1
        return True
            
