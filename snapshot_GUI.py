import tkinter as tki
from scrape_otomoto import scrape_offer_list
import shelve

class SnapshotApp:
    def __init__(self, parent):
        self.shelf = None

        self.top_container = tki.Frame(parent)
        self.top_container.pack(side=tki.TOP)

        self.list_container = tki.Frame(self.top_container)
        self.list_container.pack(side=tki.LEFT)

        self.details_container = tki.Frame(self.top_container)
        self.details_container.pack(side=tki.RIGHT)

        self.snapshot_list = tki.Listbox(self.list_container)
        self.snapshot_list.pack()

        self.button_container = tki.Frame(parent)
        self.button_container.pack(side=tki.BOTTOM)

        self.scrape_button = tki.Button(self.button_container, text="Create snapshot")
        self.scrape_button.pack(side=tki.LEFT)
        self.scrape_button.bind("<Button-1>", self.scrape_button_click)

        self.clean_button = tki.Button(self.button_container, text="Load snapshot", background="grey")
        self.clean_button.pack(side=tki.RIGHT)

    def scrape_button_click(self, event):
        self.create_snapshot()

    def create_snapshot(self):
        shelf_file = scrape_offer_list(dist=5, loc='kolo')
        self.shelf = shelve.open(shelf_file)

if __name__ == "__main__":
    root = tki.Tk()
    app = SnapshotApp(root)
    root.mainloop()