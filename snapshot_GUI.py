import tkinter as tki
from scrape_otomoto import scrape_offer_list, scrape_photos_for_offer
import shelve
import os
from moto import motorcycle_offer
from time import sleep
from PIL import ImageTk, Image
import math

class SnapshotBrowserApp:
    def __init__(self, parent):
        self.parent = parent
        self.shelf = None
        self.index_to_id = {}
        self.image_side = 400
        self.image_size = (self.image_side, self.image_side)
        self.current_image_index = None
        self.displayed_image = ImageTk.PhotoImage(Image.open('default.jpg'))#.resize(self.image_size))

        self.top_container = tki.Frame(parent)
        self.top_container.pack(side=tki.TOP, fill=tki.BOTH, expand=True)

        self.snapshot_container = tki.Frame(self.top_container)
        self.snapshot_container.pack(side=tki.LEFT, fill=tki.Y, expand=False)

        self.details_container = tki.Frame(self.top_container)
        self.details_container.pack(side=tki.RIGHT, fill=tki.BOTH, expand=True)

        self.detail_canvas = tki.Canvas(self.details_container)
        self.detail_canvas.pack(side=tki.TOP, expand=tki.YES, fill=tki.BOTH)
        self.detail_canvas.create_image(0, 0, anchor=tki.NW, image=self.displayed_image)

        self.details_text = tki.Text(self.details_container, height=10, width=40)
        self.details_text.pack(side=tki.BOTTOM)

        self.snapshot_list = tki.Listbox(self.snapshot_container, height=40, width=50)
        self.snapshot_list.pack(side=tki.BOTTOM)
        self.current_list_selection = None

        self.snapshot_props_container = tki.Frame(self.snapshot_container)
        self.snapshot_props_container.pack(side=tki.TOP)

        self.snapshot_loc_label = tki.Label(self.snapshot_props_container, text="City")
        self.snapshot_loc_label.pack(side=tki.LEFT)

        self.snapshot_loc_entry = tki.Entry(self.snapshot_props_container)
        self.snapshot_loc_entry.pack(side=tki.LEFT)
        self.snapshot_loc_entry.insert(tki.END, 'kolo')

        self.snapshot_dist_label = tki.Label(self.snapshot_props_container, text="Radius")
        self.snapshot_dist_label.pack(side=tki.LEFT)

        self.snapshot_dist_entry = tki.Entry(self.snapshot_props_container)
        self.snapshot_dist_entry.pack(side=tki.RIGHT)
        self.snapshot_dist_entry.insert(tki.END, '5')

        self.button_container = tki.Frame(parent)
        self.button_container.pack(side=tki.BOTTOM)

        self.scrape_button = tki.Button(self.button_container, text="Create snapshot")
        self.scrape_button.pack(side=tki.LEFT)
        self.scrape_button.bind("<Button-1>", self.scrape_button_click)

        self.clean_button = tki.Button(self.button_container, text="Load snapshot", background="grey")
        self.clean_button.pack(side=tki.RIGHT)

        self.offer_list_poll()

    def __del__(self):
        if self.shelf is not None:
            self.shelf.close()

    def scrape_button_click(self, event):
        self.create_snapshot()

    def create_snapshot(self):
        dist = int(self.snapshot_dist_entry.get())
        loc = self.snapshot_loc_entry.get()
        shelf_file = scrape_offer_list(dist=dist, loc=loc)
        self.shelf = shelve.open(shelf_file)
        id_list = self.shelf.keys()
        self.snapshot_list.delete(1, tki.END)
        for index, id in enumerate(id_list):
            self.snapshot_list.insert(index, self.shelf[id])
            self.index_to_id[index] = id

    def offer_list_poll(self):
        current_list_selection = self.snapshot_list.curselection()
        if current_list_selection is not self.current_list_selection:
            self.print_details(current_list_selection)
            self.display_image(current_list_selection)
            self.current_list_selection = current_list_selection
        self.parent.after(250, self.offer_list_poll)
    
    def print_details(self, index):
        if len(index) > 0:
            moto = self.shelf[self.index_to_id[index[0]]]
            self.details_text.delete(1.0, tki.END)
            self.details_text.insert(tki.END, moto.pretty_str())

    def display_image(self, offer_index, image_index=0):
        if len(offer_index) > 0:
            moto = self.shelf[self.index_to_id[offer_index[0]]]
            scrape_photos_for_offer(moto)
            image_filename = f'data/{moto.moto_id}/img{image_index}.jpg'
            if os.path.isfile(image_filename):
                max_width = self.detail_canvas.winfo_width()
                max_height = self.detail_canvas.winfo_height()
                max_ratio = max_width / max_height
                image = Image.open(image_filename)
                image_ratio = image.width / image.height
                if image_ratio > max_ratio:
                    image = image.resize((max_width, math.floor(max_width / image_ratio)))
                else:
                    image = image.resize((math.floor(max_height * image_ratio), max_height))
                self.displayed_image = ImageTk.PhotoImage(image)
                self.detail_canvas.create_image(math.floor(max_width / 2), math.floor(max_height / 2), anchor=tki.CENTER, image=self.displayed_image)

if __name__ == "__main__":
    root = tki.Tk()
    app = SnapshotBrowserApp(root)
    root.mainloop()