from scrape_otomoto import scrape_offer_list
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', "--location", type=str)
    parser.add_argument('-d', "--distance", type=int, default=5)
    parser.add_argument("-f", "--shelf_file", type=str, default=None)
    parser.add_argument("-sd", "--details", action='store_true', default=False)
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    parser.add_argument("-o", "--overwrite", action='store_true', default=False)
    parser.add_argument("-p", "--photos", action='store_true', default=False)
    args = parser.parse_args()
    
    shelf_file = args.shelf_file
    if shelf_file is not None:
        shelf_file = shelf_file.strip()
        
    scrape_offer_list(
        args.distance,
        args.location.strip(),
        shelf_name=shelf_file,
        scrape_details=args.details,
        verbose_switch=args.verbose,
        overwrite=args.overwrite,
        scrape_photos=args.photos
    )