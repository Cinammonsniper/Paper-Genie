import contextlib
import customtkinter
from DownloadAgent import DownloadAgent
from SubjectInfo import Subject
from tkinter import RIGHT, Y, BOTH, DISABLED, NORMAL, END
import threading
from PIL import Image
import tkinter as tk
from tkinter import ttk
from Scrapper import Fetcher
import os
from SimilaritySearch import SimilaritySearch


def get_theme():
    root_path = os.getcwd()
    path = f"{root_path}\\assets\\theme.json"
    return (True, path) if os.path.exists(path) is True else (False, "")


class CreateGUI:
    def __init__(self) -> None:
        self.accent_1 = "#242526"
        self.accent_2 = "#18191A"
        
        self.background = "#121212"
        self.frame_colour = "#18191A"
        self.fore_ground = "#3D3D3D"
        self.border = "#818181"
        self.text_col = "#E4E6EB"
        self.second_text_col = "#B0B3B8"
        
        self.lh = 20
        self.lw = 10
        
        self.subjects:dict
        self.current_subject:Subject
        self.variant_list = []
        self.paper_list = []
        self.initialize()
    
    def initialize(self):
        exists, path = get_theme()
        customtkinter.set_default_color_theme(path)
        customtkinter.set_appearance_mode("dark")
        return exists
        
    def create_table(self):
        style = ttk.Style(self.app)
        style.theme_use("alt")
        style.configure("Treeview", 
                        background=self.fore_ground,
                        foreground=self.text_col, 
                        fieldbackground=self.fore_ground,
                        rowheight=31,
                        font=('Roboto', 13 ,'bold'))
        style.configure("Treeview.Heading",
                        background=self.background,
                        foreground=self.text_col,
                        font=('Roboto', 13 ,'bold'))
        self.table = ttk.Treeview(self.table_frame, columns=["Subject Name", "Subject Code"], show='headings', height=15)
        self.table.heading("Subject Name", text="Subject Name")
        self.table.heading("Subject Code", text="Subject Code")
        self.tablescroll = customtkinter.CTkScrollbar(self.table_frame, command=self.table.yview, fg_color=self.background, bg_color=self.background)
        self.tablescroll.pack(side= RIGHT, fill= Y)
        self.table.pack(fill=BOTH, expand=1)
        self.tablescroll.configure(command=self.table.yview)
        self.table.configure(yscrollcommand=self.tablescroll.set)
    
    def fill_table(self, subjects: dict[str,Subject], no_results: bool):
        if not no_results:    
            for code in subjects:
                value = (subjects[code].name, str(code))
                self.table.insert(parent="", index=END, iid=str(code), values=value)
        else:
            value = ("No Matches Found!", "")
            self.table.insert(parent="", index=END, iid="0", values=value)
        
    def clear_table(self):
        with contextlib.suppress(AttributeError):
            self.table.destroy()
            self.tablescroll.destroy()
    
    def alevel(self):
        self.clear_option_menu()
        self.clear_table()
        self.create_table()
        self.fetcher = Fetcher("A levels")
        self.subjects = self.fetcher.fetch_subject_list() 
        self.fill_table(self.subjects, False)
        self.alevel_button.configure(state=DISABLED)
        self.olevel_button.configure(state=NORMAL)
        self.igcse_button.configure(state=NORMAL)
        self.search_button.configure(state=NORMAL)
        
    def olevel(self):
        self.clear_option_menu()
        self.clear_table()
        self.create_table()
        self.fetcher = Fetcher("O levels")
        self.subjects = self.fetcher.fetch_subject_list() 
        self.fill_table(self.subjects, False)
        self.alevel_button.configure(state=NORMAL)
        self.olevel_button.configure(state=DISABLED)
        self.igcse_button.configure(state=NORMAL)
        self.search_button.configure(state=NORMAL)
        
    def igcse(self):
        self.clear_option_menu()
        self.clear_table()
        self.create_table()
        self.fetcher = Fetcher("IGCSE")
        self.subjects = self.fetcher.fetch_subject_list() 
        self.fill_table(self.subjects, False)
        self.alevel_button.configure(state=NORMAL)
        self.olevel_button.configure(state=NORMAL)
        self.igcse_button.configure(state=DISABLED)
        self.search_button.configure(state=NORMAL)
    
    def create_option_menu(self):
        year_range_str = [str(value) for value in self.current_subject.year_range]
        self.start_dropdown.configure(values=year_range_str)
        self.end_dropdown.configure(values=year_range_str)
        self.start_dropdown.set(year_range_str[0])
        self.end_dropdown.set(year_range_str[-1])
        self.variant_check_box_list = []
        self.paper_checkbox_list = []
        y_value = 110 
        for i in self.current_subject.variants:
            check_box = customtkinter.CTkCheckBox(self.range_frame, text=str(i), onvalue="1", offvalue="0", font=('Roboto', 15 ,'bold'))
            check_box.place(x=20, y = y_value)
            y_value += 40
            self.variant_check_box_list.append(check_box)
        
        y_value = 110
        for i in self.current_subject.papers:
            check_box = customtkinter.CTkCheckBox(self.range_frame, text=str(i), onvalue="1", offvalue="0", font=('Roboto', 15 ,'bold'))
            check_box.place(x=180, y = y_value)
            y_value += 40
            self.paper_checkbox_list.append(check_box)
            
    def download_files(self):
        start_year = int(self.start_dropdown.get())
        end_year = int(self.end_dropdown.get())
        self.variant_list = []
        self.paper_list = []
        for check_box in self.variant_check_box_list:
            if int(check_box.get()) == 1:
                self.variant_list.append(int(check_box.cget("text")))

        for check_box in self.paper_checkbox_list:
            if int(check_box.get()) == 1:
                self.paper_list.append(int(check_box.cget("text")))
        if self.paper_list != [] and self.variant_list != []:
            self.execute_downloads(start_year, end_year)

    def execute_downloads(self, start_year, end_year):
        state_list = self.disable_buttons()
        self.done_label = customtkinter.CTkLabel(self.range_frame, text="Downloading...", font=('Roboto', 14 ,'bold'))
        self.done_label.place(x=195, y=330)
        thread = threading.Thread(target=self.download, args=(start_year,end_year, state_list,))
        thread.start()

    def download(self, start_year, end_year, state_list):
        session = DownloadAgent((start_year, end_year), self.variant_list, self.paper_list, self.current_subject.code, self.current_subject)
        attribute_state = session.initialize()
        if attribute_state is True:
            done = session.download_papers()
            if done == True:
                self.done_label.configure(text="Downloaded")
                self.done_label.after(3000, lambda: self.done_label.destroy())
        self.enable_buttons(state_list)

    
    def clear_option_menu(self):
        with contextlib.suppress(AttributeError, ValueError):
            if len(self.variant_check_box_list) > 0:
                for check_box in self.variant_check_box_list:
                    check_box.destroy()
            if len(self.paper_checkbox_list) > 0:
                for check_box in self.paper_checkbox_list:
                    check_box.destroy()
            self.start_dropdown.configure(values=[""])
            self.end_dropdown.configure(values=[""])
            self.start_dropdown.set("")
            self.end_dropdown.set("")
            self.variant_list = []
            self.paper_list = []
        

    def search(self):
        with contextlib.suppress(AttributeError):
            subject_code = None
            if len(self.table.selection()) > 0:
                subject_code = self.table.selection()[0]
                if subject_code is not None:
                    self.clear_option_menu()
                    state_list = self.disable_buttons()
                    thread = threading.Thread(target=self.set_up_search,args=(subject_code,state_list,))
                    thread.start()
    
    def disable_buttons(self):
        state_list = [self.alevel_button.cget("state"), self.olevel_button.cget("state"), self.igcse_button.cget("state"), self.select_button.cget("state"), self.download_button.cget("state")]
        self.select_button.configure(state=DISABLED)
        self.download_button.configure(state=DISABLED)
        self.alevel_button.configure(state=DISABLED)
        self.olevel_button.configure(state=DISABLED)
        self.igcse_button.configure(state=DISABLED)
        return state_list
        
    def enable_buttons(self, state_list):
        self.select_button.configure(state=state_list[3])
        self.download_button.configure(state=state_list[4])
        self.alevel_button.configure(state=state_list[0])
        self.olevel_button.configure(state=state_list[1])
        self.igcse_button.configure(state=state_list[2])

    
    def set_up_search(self, subject_code, button_states):
        comp_check, self.subjects = self.fetcher.fetch_paper_range(str(subject_code)) # type: ignore
        if comp_check is False:
            warning_label = customtkinter.CTkLabel(self.range_frame, text="The subject is unsupported", font=('Roboto', 16 ,'bold'))
            warning_label.place(x=50, y=150)
            warning_label.after(2000, lambda: warning_label.destroy()) 
        else:
            self.subjects = self.fetcher.fetch_paper_info(str(subject_code))
            self.current_subject = self.subjects[subject_code]
            button_states[4] = NORMAL
            self.create_option_menu()
        self.enable_buttons(button_states)
        
    def search_code(self):
        subject_dict = {}
        text = self.search_bar.get()
        
        if text.isdigit() and len(text) == 4:
            for subject_code in list(self.subjects.keys()):
                if int(subject_code) == int(text):
                    subject_dict = {subject_code: self.subjects[subject_code]}
        elif text.isdigit():
            subject_dict = {}
        elif text == "":
            subject_dict = self.subjects
        else:
            similarity_check = SimilaritySearch(self.subjects, text)
            subject_dict = similarity_check.process()
        self.clear_table()
        self.create_table()
        if len(subject_dict) == 0:
            self.fill_table({}, True)
        else:
            self.fill_table(subject_dict, False)


    def main_window(self):
        self.app = customtkinter.CTk()
        self.app.geometry("860x650")
        self.app.resizable(height=False, width=False)
        self.app.iconbitmap("assets\\icon.ico")
        self.app.title("Paper Genie")
        self.table_frame = customtkinter.CTkFrame(self.app, width=400, height=496)
        self.table_frame.place(x=50, y=106)
        
        self.search_bar_frame = customtkinter.CTkFrame(self.app, width=400, height=45, fg_color=self.background)
        self.search_bar_frame.place(x=50, y=50)
        
        self.search_bar = customtkinter.CTkEntry(self.search_bar_frame, width=350, height=30, font=('Roboto', 15))
        search_image = customtkinter.CTkImage(dark_image=Image.open("assets\\search.png"),size=(15, 15))
        self.search_button = customtkinter.CTkButton(self.search_bar_frame, text="", image=search_image, width=40, height=30, fg_color="#3D3D3D", border_color="#818181", border_width=2, command=self.search_code, hover_color="#777777", state=DISABLED)
        self.search_bar.place(x=0, y=0)
        self.search_button.place(x=360, y=0)
        
        self.top_button_frame = customtkinter.CTkFrame(self.app, width=310, height=100)
        self.top_button_frame.place(x=500, y=50)
        
        self.alevel_button = customtkinter.CTkButton(self.top_button_frame, text="A level",width=90, height=50, command=self.alevel, font=('Roboto', 20 ,'bold'))
        self.olevel_button = customtkinter.CTkButton(self.top_button_frame, text="O level",width=90, height=50, command=self.olevel, font=('Roboto', 20 ,'bold'))
        self.igcse_button = customtkinter.CTkButton(self.top_button_frame, text="IGCSE",width=90, height=50, command=self.igcse, font=('Roboto', 20 ,'bold'))
        self.alevel_button.place(x=10, y=25)
        self.olevel_button.place(x=110, y=25)
        self.igcse_button.place(x=210, y=25)
        
        self.range_frame = customtkinter.CTkFrame(self.app, width=310, height=427)
        self.range_frame.place(x=500, y=175)
        download_image = customtkinter.CTkImage(dark_image=Image.open("assets\\download.png"),size=(30, 30)) # type: ignore
        select_image = customtkinter.CTkImage(dark_image=Image.open("assets\\expand.png"),size=(30, 30)) # type: ignore
        self.select_button = customtkinter.CTkButton(self.range_frame, image=select_image, text="", width=50, height=50, command=self.search)
        self.download_button = customtkinter.CTkButton(self.range_frame, image=download_image,width=50, text="", height=50, state=DISABLED, command=self.download_files)
        self.range_label = customtkinter.CTkLabel(self.range_frame, text="Range: ", font=('Roboto', 20 ,'bold'))
        self.to_label = customtkinter.CTkLabel(self.range_frame, text="to", font=('Roboto', 12 ,'bold'))
        self.start_dropdown = customtkinter.CTkOptionMenu(self.range_frame, values=[""], width=130, font=('Roboto', 15 ,'bold'))
        self.end_dropdown = customtkinter.CTkOptionMenu(self.range_frame, values=[""], width=130, font=('Roboto', 15 ,'bold'))
        self.variants_label = customtkinter.CTkLabel(self.range_frame, text="Variants", font=('Roboto', 20 ,'bold'))
        self.papers_label = customtkinter.CTkLabel(self.range_frame, text="Papers", font=('Roboto', 20 ,'bold'))
        
        self.range_label.place(x=10, y=10)
        self.start_dropdown.place(x=10, y=45)
        self.to_label.place(x=150, y=45)
        self.end_dropdown.place(x=170, y=45)
        
        self.variants_label.place(x=10, y=80) 
        self.papers_label.place(x=180, y=80)
        
        self.select_button.place(x=190, y=365)
        self.download_button.place(x=250, y=365)
        
        self.app.mainloop()

def main():
    gui = CreateGUI()
    exists = gui.initialize()
    if exists is True:
        gui.main_window()

main()
