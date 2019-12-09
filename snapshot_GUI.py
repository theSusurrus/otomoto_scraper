import tkinter as tki
import tkinter.ttk as ttk
import tkinter.filedialog
from scrape_otomoto import scrape_offer_list, scrape_details_for_offer
import shelve
import os
import shutil
from moto import motorcycle_offer
from time import sleep
from PIL import ImageTk, Image
import math
import glob
import threading
import time
import queue

class SnapshotBrowserApp:
    def __init__(self, parent):
        self.parent = parent
        self.shelf = None
        self.shelf_ready_event = threading.Event()
        self.shelf_name = None
        self.scraping_in_progress = False
        self.progress_queue = queue.Queue()
        self.index_to_id = {}
        self.current_moto = None
        self.current_image_index = 0
        self.details_update_pending = False
        self.canvas_ratio = 1.0
        self.previous_selected_id = None
        self.raw_image = None

        self.top_container = tki.Frame(parent)
        self.top_container.pack(side=tki.TOP, fill=tki.BOTH, expand=True)

        self.snapshot_container = tki.Frame(self.top_container)
        self.snapshot_container.pack(side=tki.LEFT, fill=tki.Y, expand=False)

        self.details_container = tki.Frame(self.top_container)
        self.details_container.pack(side=tki.RIGHT, fill=tki.BOTH, expand=True)

        self.detail_canvas = tki.Canvas(self.details_container)
        self.detail_canvas.pack(side=tki.TOP, expand=tki.YES, fill=tki.BOTH)

        self.details_bottom_container = tki.Frame(self.details_container)
        self.details_bottom_container.pack(side=tki.BOTTOM, fill=tki.X, expand=False)

        self.details_text = tki.Text(self.details_bottom_container, height=15)
        self.details_text.pack(side=tki.BOTTOM, fill=tki.X, expand=True)

        self.picture_buttons_container = tki.Frame(self.details_bottom_container)
        self.picture_buttons_container.pack(side=tki.TOP)

        self.previous_picture_button = tki.Button(self.picture_buttons_container, text="<-")
        self.previous_picture_button.pack(side=tki.LEFT)
        self.previous_picture_button.bind("<Button-1>", lambda event: self.switch_picture(increment=-1))

        self.picture_label = tki.Label(self.picture_buttons_container, text=" ", width=10)
        self.picture_label.pack(side=tki.LEFT)

        self.next_picture_button = tki.Button(self.picture_buttons_container, text="->")
        self.next_picture_button.pack(side=tki.RIGHT)
        self.next_picture_button.bind("<Button-1>", lambda event: self.switch_picture(increment=1))

        self.snapshot_list = tki.Listbox(self.snapshot_container, width=50)
        self.snapshot_list.pack(side=tki.BOTTOM, fill=tki.Y, expand=True)
        self.current_list_selection = None

        self.snapshot_props_container = tki.Frame(self.snapshot_container)
        self.snapshot_props_container.pack(side=tki.TOP)

        self.button_container = tki.Frame(parent)
        self.button_container.pack(side=tki.BOTTOM, fill=tki.X)

        self.scrape_button = tki.Button(self.button_container, text="Create snapshot")
        self.scrape_button.pack(side=tki.LEFT)
        self.scrape_button.bind("<Button-1>", self.scrape_button_click)

        self.snapshot_loc_label = tki.Label(self.button_container, text="City")
        self.snapshot_loc_label.pack(side=tki.LEFT)

        self.snapshot_loc_entry = tki.Entry(self.button_container)
        self.snapshot_loc_entry.pack(side=tki.LEFT)
        self.snapshot_loc_entry.insert(tki.END, 'kolo')

        self.snapshot_dist_label = tki.Label(self.button_container, text="Radius")
        self.snapshot_dist_label.pack(side=tki.LEFT)

        self.snapshot_dist_entry = tki.Entry(self.button_container)
        self.snapshot_dist_entry.pack(side=tki.LEFT)
        self.snapshot_dist_entry.insert(tki.END, '5')

        self.scrape_details_button = tki.Button(self.button_container, text="Scrape all details")
        self.scrape_details_button.pack(side=tki.LEFT)
        self.scrape_details_button.bind("<Button-1>", self.scrape_details_button_click)

        self.load_button = tki.Button(self.button_container, text="Load snapshot")
        self.load_button.pack(side=tki.LEFT)
        self.load_button.bind("<Button-1>", self.load_button_click)

        self.clean_button = tki.Button(self.button_container, text="Delete all snapshots")
        self.clean_button.pack(side=tki.LEFT)
        self.clean_button.bind("<Button-1>", self.clean_button_click)

        self.progress_bar = ttk.Progressbar(self.button_container, length=100, mode='determinate')
        self.progress_bar.pack(side=tki.RIGHT)

        self.progress_label = tki.Label(self.button_container, text='')
        self.progress_label.pack(side=tki.RIGHT)

        self.widget_refresh()

    def __del__(self):
        if self.shelf is not None:
            self.shelf.close()

    def scrape_button_click(self, event):
        self.create_snapshot()
    
    def display_progress(self, progress_obj):
        self.progress_bar['value'] = progress_obj.progress * 100
        self.progress_label['text'] = progress_obj.description

    def scrape_details_button_click(self, event):
        for moto_index in range(self.snapshot_list.size()):
            scrape_details_for_offer(self.shelf[self.index_to_id[moto_index]])
    
    def clean_button_click(self, event):
        if self.shelf is not None:
            self.shelf.close()
            self.shelf = None
        data_dirname = 'data/'
        if os.path.isdir(data_dirname):
            shutil.rmtree(data_dirname)
        self.previous_selected_id = None
        self.construct_listbox_list()

    def load_button_click(self, event):
        if self.shelf != None:
            self.shelf.close()
        filename = tki.filedialog.askopenfilename(initialdir=os.path.dirname(os.path.abspath(__file__)))
        start_index = filename.index("data/")
        end_index = filename.index(".")
        shelf_name = filename[start_index:end_index]
        self.shelf = shelve.open(shelf_name)
        self.construct_listbox_list()

    def create_snapshot(self):
        self.current_image_index = None
        self.details_update_pending = True
        dist = int(self.snapshot_dist_entry.get())
        loc = self.snapshot_loc_entry.get()

        timestamp = time.strftime("%Y_%m_%d", time.localtime())
        if not os.path.isdir('data/'):
            os.mkdir('data/')
        db_directory = f"data/snapshot_{loc}_{dist}_{timestamp}"
        if os.path.isdir(db_directory):
            shutil.rmtree(db_directory)
        os.mkdir(db_directory)
        self.shelf_name = f"{db_directory}/moto_shelf"

        scraping_thread = threading.Thread(target=scrape_offer_list, args=(dist, loc, self.shelf_name, self.shelf_ready_event, self.progress_queue))
        scraping_thread.start()
        self.scraping_in_progress = True

    def construct_listbox_list(self):
        self.snapshot_list.delete(0, tki.END)
        if self.shelf is not None:
            id_list = self.shelf.keys()
            for index, id in enumerate(id_list):
                self.snapshot_list.insert(index, self.shelf[id])
                self.index_to_id[index] = id
        self.display_image()
        self.print_details()

    def widget_refresh(self):
        if self.shelf != None:
            selected_moto = self.get_selected_moto()
            if (selected_moto != self.current_moto) and (selected_moto is not None):
                self.current_moto = selected_moto
                if self.current_moto.moto_id != self.previous_selected_id:
                    self.current_image_index = 0
                    self.update_details(self.current_moto)
                    self.print_details(self.current_moto)
                    self.details_update_pending = True
                    self.previous_selected_id = self.current_moto.moto_id
            
            current_canvas_ratio = self.detail_canvas.winfo_width() / self.detail_canvas.winfo_height()
            if (current_canvas_ratio != self.canvas_ratio) or self.details_update_pending:
                if self.current_moto != None:
                    self.display_image(true_photo=True, current_moto=self.current_moto)
                    self.print_details(self.current_moto)
                else:
                    self.display_image()
                self.details_update_pending = False

        if self.scraping_in_progress:
            if self.shelf_ready_event.isSet():
                self.shelf = shelve.open(self.shelf_name)
                self.construct_listbox_list()
                self.scraping_in_progress = False
            else:
                try:
                    print("displaying progress")
                    progress = self.progress_queue.get(0)
                    self.display_progress(progress)
                except queue.Empty:
                    print("waiting on progress queue")
                    pass
        else:
            self.progress_label['text'] = '' * 20
            self.progress_bar['value'] = 0
        self.parent.after(50, self.widget_refresh)
    
    def print_details(self, moto=None):
        self.details_text.delete('1.0', tki.END)
        if moto != None:
            self.details_text.insert(tki.END, moto.pretty_str())

    def update_details(self, current_moto):
        image_filename = f'data/{current_moto.moto_id}/img{self.current_image_index}.jpg'
        if (not os.path.isfile(image_filename)) or (current_moto.description is None):
            self.current_moto = scrape_details_for_offer(current_moto)
            self.store_moto(current_moto)
            current_list_selection = self.snapshot_list.curselection()
            self.snapshot_list.delete(current_list_selection)
            self.snapshot_list.insert(current_list_selection, current_moto)
            self.raw_image = Image.open(image_filename)


    def display_image(self, true_photo=False, current_moto=None):
        canvas_width = self.detail_canvas.winfo_width()
        canvas_height = self.detail_canvas.winfo_height()
        self.canvas_ratio = canvas_width / canvas_height
        if true_photo and (self.raw_image is not None):
            image_ratio = self.raw_image.width / self.raw_image.height
            new_size = None
            if image_ratio > self.canvas_ratio:
                new_size = (canvas_width, math.floor(canvas_width / image_ratio))
            else:
                new_size = (math.floor(canvas_height * image_ratio), canvas_height)
            resized_image = self.raw_image.resize(new_size)
            self.displayed_image = ImageTk.PhotoImage(resized_image)
        else:
            image_side = int(min(canvas_height, canvas_width))
            self.displayed_image = ImageTk.PhotoImage(Image.open('default.jpg').resize((image_side, image_side)))
        self.detail_canvas.create_image(math.floor(canvas_width / 2), math.floor(canvas_height / 2), anchor=tki.CENTER, image=self.displayed_image)

        picture_count = self.count_pictures()
        if picture_count > 0:
            picture_label_text = f'{self.current_image_index + 1} / {picture_count}'
        else:
            picture_label_text = '-'
        self.picture_label['text'] = picture_label_text

    def switch_picture(self, increment=1):
        if self.current_moto is not None:
            image_filename = f'data/{self.current_moto.moto_id}/img{self.current_image_index + increment}.jpg'
            if os.path.isfile(image_filename):
                self.raw_image = Image.open(image_filename)
                self.current_image_index += increment
                self.details_update_pending = True

    def count_pictures(self):
        counter = 0
        if self.current_moto != None:
            while os.path.isfile(f'data/{self.current_moto.moto_id}/img{counter}.jpg'):
                counter += 1
            return counter
        else:
            return 0

    def get_selected_moto(self):
        result = None
        current_list_selection = self.snapshot_list.curselection()
        if len(current_list_selection) > 0:
            result = self.shelf[self.index_to_id[current_list_selection[0]]]
        return result

    def store_moto(self, moto):
        if moto is not None:
            self.shelf[str(moto.moto_id)] = moto
        else:
            del self.shelf[str(moto.moto_id)]

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    root = tki.Tk()
    app = SnapshotBrowserApp(root)
    root.mainloop()