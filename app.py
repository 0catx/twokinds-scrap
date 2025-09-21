# *
# * Copyright (C) 2025 0catx.gay
# * This file is part of twokinds-scrap.
# *
# * twokinds-scrap is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * any later version.
# *

import requests
from bs4 import BeautifulSoup
import os
import glob
import time
import argparse
import logging
from tqdm import tqdm  # For progress bar

if os.path.isfile("./comic_downloader.log"):
    os.remove("./comic_downloader.log")

# Configure logging
logging.basicConfig(filename='comic_downloader.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bulkcounter = 0
bulklimit = 10
comicnum = 0
pathlo = "./download/"
wasError = 0
wasThereCopies = 0
whatCopies = ""

def getdata(url):
    global wasError

    try:
        r = requests.get(url, timeout=10)  # Add timeout
        r.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return r.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        print(f"Error fetching URL {url}: {e}")
        wasError = 1
        exit()

def download_image(image_url, save_path):
    global bulkcounter
    global wasError

    try:
        response = requests.get(image_url, stream=True, timeout=10) # stream=True for large files
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): # Download in chunks
                f.write(chunk)
        bulkcounter += 1
        logging.info(f"Downloaded: {save_path}")
    except requests.exceptions.RequestException as e:
        logging.exception(f"Failed to download {image_url}: {e}")
        print(f"Failed to download {image_url}: {e}")
        wasError = 1

def scrap(comicnum):
    global wasError

    htmldata = getdata("https://twokinds.keenspot.com/comic/" + str(comicnum))
    if htmldata:
        soup = BeautifulSoup(htmldata, 'html.parser')
        for item in soup.find_all('img'):
            img_url = item.get('src')
            if img_url and img_url.startswith("https://cdn.twokinds.keenspot.com/comics/"):
                image_name = os.path.basename(img_url)
                save_path = os.path.join(pathlo + "comic-" + str(comicnum) + "-" + image_name)
                if os.path.exists(save_path):
                    logging.warning(f"Double check failed: File already exists: {save_path}. First check didn't didn't notice something odd, skipping download.")
                else:
                    download_image(img_url, save_path)
    else:
        wasError = 1
        logging.exception(f"Skipping comic {comicnum} due to error fetching data.")
        print(f"Skipping comic {comicnum} due to error fetching data.")

def downloader(comicnum):
        if glob.glob(os.path.join(pathlo + "comic-" + str(comicnum) + "*")):
            global whatCopies
            global wasThereCopies

            wasThereCopies = 1
            whatCopies += str(comicnum) + ","
            logging.info(f"Skiping, {comicnum} exists. {pathlo} comic-{comicnum}")
        else:
            logging.info(f"Downloading Comic {comicnum}.")
            scrap(comicnum)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download comics from Two Kinds.")
    parser.add_argument("--start", type=int, default=1100, help="Starting range")
    parser.add_argument("--end", type=int, default=1265, help="Ending comic number")
    parser.add_argument("--path", type=str, default="./download/", help="Download directory, defaults to `./download`")
    parser.add_argument("--wait", type=int, default=10, help="How long to wait in seconds after each batch. 0 to disable. If limit is 0, this is not applicable")
    parser.add_argument("--limit", type=int, default=10, help="The limit of downloads per batch. 0 to disable. If wait is 0, this is not applicable")

    args = parser.parse_args()

    pathlo = args.path
    start = args.start
    end = args.end
    wait = args.wait
    bulklimit = args.limit

    if wait < 0:
        print("Wait ivalid")
        exit()

    if start <= 0 or end <= 0 or end < start or start > end:
        print("Range invlid")
        exit()

    if bulklimit < 0:
        print("Limit invlid")
        exit()

    if os.access(pathlo, os.W_OK) == False:
        if os.path.isdir(pathlo):
            print("Location Write Premission error: " + pathlo )
            exit()
        else:
            os.makedirs(pathlo, exist_ok=True) # Create the directory if it doesn't exist

    if wait == 0:
        logging.info(f"Downloading without wait at `{pathlo}`...")
        print("Downloading without wait...")
        
    if wait > 0:
        logging.info(f"Downloading with wait, {wait} with a batch limit of {bulklimit} at  `{pathlo}`...")
        print(f"Downloading with wait, {wait} with a batch limit of {bulklimit} at `{pathlo}`...")

    for number in tqdm(range(start, end + 1), desc="Processing Comics"): # Use tqdm for progress
        comicnum = number
        if wait == 0 or bulklimit == 0:
            downloader(comicnum)
        if wait > 0:
            if bulkcounter < bulklimit:
                downloader(comicnum)
            if bulkcounter == bulklimit:
                print(f"Waiting {wait} seconds")
                logging.info(f"Waiting {wait} seconds")
                time.sleep(wait)
                logging.info("Resuming...")
                print("Resuming...")
                bulkcounter = 0
                downloader(comicnum)
        else:
            print("Wait invalid")
            exit()
    
    if wasError == 1:
        print("Done with errors: Check logs.")
        if wasThereCopies == 1:
            print("Some comics already existed: " + whatCopies)
        exit()
    else:
        print("Done. Logs available.")
        if wasThereCopies == 1:
            print("Some comics already existed: " + whatCopies)
        exit()