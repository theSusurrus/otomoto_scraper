import tkinter as tki
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

class SnapshotBrowserApp:
    def __init__(self, parent):
        self.parent = parent
        self.shelf = None
        self.index_to_id = {}
        self.current_image_index = 0
        self.image_update_pending = False
        self.canvas_ratio = 1.0
        self.current_moto = None

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
        self.previous_picture_button.bind("<Button-1>", self.switch_previous_picture)

        self.picture_label = tki.Label(self.picture_buttons_container, text=" ", width=10)
        self.picture_label.pack(side=tki.LEFT)

        self.next_picture_button = tki.Button(self.picture_buttons_container, text="->")
        self.next_picture_button.pack(side=tki.RIGHT)
        self.next_picture_button.bind("<Button-1>", self.switch_next_picture)

        self.snapshot_list = tki.Listbox(self.snapshot_container, width=50)
        self.snapshot_list.pack(side=tki.BOTTOM, fill=tki.Y, expand=True)
        self.current_list_selection = None

        self.snapshot_props_container = tki.Frame(self.snapshot_container)
        self.snapshot_props_container.pack(side=tki.TOP)

        self.button_container = tki.Frame(parent)
        self.button_container.pack(side=tki.BOTTOM)

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
        self.load_button.pack(side=tki.RIGHT)
        self.load_button.bind("<Button-1>", self.load_button_click)

        self.clean_button = tki.Button(self.button_container, text="Delete all snapshots")
        self.clean_button.pack(side=tki.RIGHT)
        self.clean_button.bind("<Button-1>", self.clean_button_click)

        self.offer_list_poll()

    def __del__(self):
        if self.shelf is not None:
            self.shelf.close()

    def scrape_button_click(self, event):
        self.create_snapshot()

    def scrape_details_button_click(self, event):
        for moto_index, moto_str in enumerate(self.snapshot_list.get(0, tki.END)):
            scrape_details_for_offer(self.shelf[self.index_to_id[moto_index]])
    
    def clean_button_click(self, event):
        shutil.rmtree('data/')

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
        self.current_moto = None
        self.image_update_pending = True
        dist = int(self.snapshot_dist_entry.get())
        loc = self.snapshot_loc_entry.get()
        shelf_file = scrape_offer_list(dist=dist, loc=loc)
        self.shelf = shelve.open(shelf_file)
        self.construct_listbox_list()

    def construct_listbox_list(self):
        id_list = self.shelf.keys()
        self.snapshot_list.delete(1, tki.END)
        for index, id in enumerate(id_list):
            self.snapshot_list.insert(index, self.shelf[id])
            self.index_to_id[index] = id

    def offer_list_poll(self):
        current_list_selection = self.snapshot_list.curselection()
        if current_list_selection != self.current_list_selection:
            self.current_image_index = 0
            if len(current_list_selection) > 0:
                self.current_moto = self.shelf[self.index_to_id[current_list_selection[0]]]
                self.print_details(self.current_moto)
                self.current_list_selection = current_list_selection
                self.image_update_pending = True
            else:
                self.current_moto = None
        
        current_canvas_ratio = self.detail_canvas.winfo_width() / self.detail_canvas.winfo_height()
        if (current_canvas_ratio != self.canvas_ratio) or self.image_update_pending:
            if self.current_moto != None:
                self.display_image(True)
                self.image_update_pending = False
                picture_count = self.count_pictures()
                if picture_count > 0:
                    picture_label_text = f'{self.current_image_index + 1} / {picture_count}'
                else:
                    picture_label_text = '-'
                self.picture_label['text'] = picture_label_text
            else:
                self.display_image(False)

        self.parent.after(50, self.offer_list_poll)
    
    def print_details(self, moto):
        self.details_text.delete(1.0, tki.END)
        self.details_text.insert(tki.END, moto.pretty_str())

    def display_image(self, true_photo):
        canvas_width = self.detail_canvas.winfo_width()
        canvas_height = self.detail_canvas.winfo_height()
        self.canvas_ratio = canvas_width / canvas_height
        if true_photo:
            scrape_details_for_offer(self.current_moto)
            self.print_details(self.current_moto)
            image_filename = f'data/{self.current_moto.moto_id}/img{self.current_image_index}.jpg'
            if os.path.isfile(image_filename):
                image = Image.open(image_filename)
                image_ratio = image.width / image.height
                if image_ratio > self.canvas_ratio:
                    image = image.resize((canvas_width, math.floor(canvas_width / image_ratio)))
                else:
                    image = image.resize((math.floor(canvas_height * image_ratio), canvas_height))
                self.displayed_image = ImageTk.PhotoImage(image)
        else:
            image_side = int(min(canvas_height, canvas_width))
            self.displayed_image = ImageTk.PhotoImage(Image.open('default.jpg').resize((image_side, image_side)))
        self.detail_canvas.create_image(math.floor(canvas_width / 2), math.floor(canvas_height / 2), anchor=tki.CENTER, image=self.displayed_image)

    def switch_next_picture(self, event):
        image_filename = f'data/{self.current_moto.moto_id}/img{self.current_image_index + 1}.jpg'
        if os.path.isfile(image_filename):
            self.current_image_index += 1
            self.image_update_pending = True

    def switch_previous_picture(self, event):
        image_filename = f'data/{self.current_moto.moto_id}/img{self.current_image_index - 1}.jpg'
        if os.path.isfile(image_filename):
            self.current_image_index -= 1
            self.image_update_pending = True

    def count_pictures(self):
        counter = 0
        if self.current_moto != None:
            while os.path.isfile(f'data/{self.current_moto.moto_id}/img{counter}.jpg'):
                counter += 1
            return counter
        else:
            return 0

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    root = tki.Tk()
    app = SnapshotBrowserApp(root)
    root.mainloop()