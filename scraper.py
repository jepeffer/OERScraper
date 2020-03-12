from bs4 import BeautifulSoup
import requests
import time
import zipfile
import io
import os
from os.path import basename, join

BASE_URL = "https://www.oercommons.org/browse?batch_size=100&sort_by=title&view_mode=summary&f.general_subject=life-science"
SAVE_PATH = "C:\\Users\\myhog\\Desktop\\Resources\\"

# Grabs all the HTML from the BASE_URL and parses it based on the class name below... item-link...
# These links will provide links to our resources we need!
def scrape_base_page():
    print("Now scraping: ", BASE_URL)
    r  = requests.get(BASE_URL)
    data = r.text
    soup = BeautifulSoup(data,"html.parser")
    all_links = []

    for link in soup.find_all('a', class_ = "item-link js-item-link"):
        all_links.append(link.get('href'))
    
    for link in all_links:
      #  time.sleep(2) # We are nice web scrapers...
        print ("#####################################")
        gotoResource(link)
    
# Goes to the specific resource link. This page is the before page for the download/creation of the resource
def gotoResource(link_in):
    r = requests.get(link_in)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    resource_link = [] # Should only be one link, but it may be more
   
    for link in soup.find_all('a', class_ = "view-resource-link btn btn-primary js-save-search-parameters"):
        resource_link.append(link.get('href'))
   
    print("Resource found: ", resource_link)
    
    for link in resource_link:
       # time.sleep(2) # We are nice web scrapers...
        decideResource(link)
 
# Links are either downloads, or they are just webpages, I will attempt to download and or build my own resource based on the webpages
# This is not always guaranteed success
def decideResource(link_in):
    print("Attemping to decide the resource: ", link_in)
    r = requests.get(link_in)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    figures = [] # Should only be one, but may be more
                 # Download hrefs are stored in figures
                
    for link in soup.find_all('figure', class_ = "download"):
        figures.append(link)
    
    if (figures != []):
        print ("Download link found!")
        print ("Now attempting to download!")
        downloadResource(figures)
    else:
        print ("No download link, now attempting to build the resource by scraping the individual page's html")
        buildResource(soup)

    
# If the resource has a download link it should come to this method!
def downloadResource(figures_in):
    download_link = [] # Parsed from the figure
    link_titles = [] # Parsed from figure, used to tell the file type
    for figure in figures_in:
        link_title = figure.find('a').contents[0]
        link = figure.find('a')['href']
        download_link.append(link)
        link_titles.append(link_title)
    
    print("Download link(s) found: ", download_link)
    file_type = ''
    new_dir = ''
    
    for title in link_titles:
        print ("Title of the resource:", title)
        file_type = getFileType(title)
        new_dir = createNewFolder(title)
    
    for download in download_link:
        print ("Attempting to download: ", download)
        if file_type == "zip":
            downloadZIP(download, new_dir)
        elif file_type == "pdf":
            downloadPDF(download, link_titles[0], new_dir)
        else:
            print ("Unknown file type: ", file_type, " Now skipping.")
        
# If the resource is not a download, then we have to scrape the page and its html elements
def buildResource(download_in):
    print("Not implemented")

# This method determines the file type by the title of the file
def getFileType(title_in):
    return title_in[-3:].lower()
    
# Downloads the a ZIP file
def downloadZIP(download_in, new_dir_in):
    r = requests.get(download_in, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(new_dir_in)
    
# Downloads a PDF file
def downloadPDF(download_in, title_in, new_dir_in):
    response = requests.get(download_in)
    with open(join(new_dir_in, title_in), 'wb') as f:
        f.write(response.content)
        
# Creates a new folder where I can put the download resource and the meta data for said resource
def createNewFolder(title_in):
    new_dir = SAVE_PATH + title_in[:-4] # Remove the file type
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    return new_dir


if __name__ == '__main__':
    scrape_base_page()