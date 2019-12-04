import tkinter as tki
from scrape_otomoto import scrape_offer_list
import shelve

class SnapshotApp:
    def __init__(self, parent):
        self.shelf = None

        self.top_container = tki.Frame(parent)
        self.top_container.pack(side=tki.TOP)

        self.snapshot_container = tki.Frame(self.top_container)
        self.snapshot_container.pack(side=tki.LEFT)

        self.details_container = tki.Frame(self.top_container)
        self.details_container.pack(side=tki.RIGHT)

        self.snapshot_list = tki.Listbox(self.snapshot_container, height=40, width=50)
        self.snapshot_list.pack(side=tki.BOTTOM)

        self.snapshot_props_container = tki.Frame(self.snapshot_container)
        self.snapshot_props_container.pack(side=tki.TOP)

        self.snapshot_loc_label = tki.Label(self.snapshot_props_container, text="City")
        self.snapshot_loc_label.pack(side=tki.LEFT)

        self.snapshot_loc_entry = tki.Entry(self.snapshot_props_container)
        self.snapshot_loc_entry.pack(side=tki.LEFT)

        self.snapshot_dist_label = tki.Label(self.snapshot_props_container, text="Radius")
        self.snapshot_dist_label.pack(side=tki.LEFT)

        self.snapshot_dist_entry = tki.Entry(self.snapshot_props_container)
        self.snapshot_dist_entry.pack(side=tki.RIGHT)

        self.button_container = tki.Frame(parent)
        self.button_container.pack(side=tki.BOTTOM)

        self.scrape_button = tki.Button(self.button_container, text="Create snapshot")
        self.scrape_button.pack(side=tki.LEFT)
        self.scrape_button.bind("<Button-1>", self.scrape_button_click)

        self.clean_button = tki.Button(self.button_container, text="Load snapshot", background="grey")
        self.clean_button.pack(side=tki.RIGHT)

    def __del__(self):
        if self.shelf is not None:
            self.shelf.close()

    def scrape_button_click(self, event):
        self.create_snapshot()

    def create_snapshot(self):
        shelf_file = scrape_offer_list(dist=5, loc='lodz')
        self.shelf = shelve.open(shelf_file)
        id_list = self.shelf.keys()
        for index, id in enumerate(id_list):
            self.snapshot_list.insert(index, self.shelf[id])

if __name__ == "__main__":
    root = tki.Tk()
    app = SnapshotApp(root)
    root.mainloop()