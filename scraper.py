from bs4 import BeautifulSoup
import requests
import time
import zipfile
import io
import os
from os.path import basename, join

BASE_URL = "https://www.oercommons.org/browse?batch_size=100&sort_by=title&view_mode=summary&f.general_subject=life-science"
SAVE_PATH = "C:\\Users\\myhog\\Desktop\\School\\Capstone\\Resources\\"

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
        time.sleep(2) # We are nice web scrapers...
        print ("#####################################")
        gotoResource(link)
    
# Goes to the specific resource link. This page is the before page for the download/creation of the resource
def gotoResource(link_in):
    r = requests.get(link_in)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    resource_link = [] # Should only be one link, but it may be more
   
    new_dir = createNewDir(soup)  
    extractMetaData(soup, new_dir)
   
    for link in soup.find_all('a', class_ = "view-resource-link btn btn-primary js-save-search-parameters"):
        resource_link.append(link.get('href'))
   
    print("Resource found: ", resource_link)

    for link in resource_link:
        time.sleep(2) # We are nice web scrapers...
        decideResource(link, new_dir)
   
# Find the title of the new dir and then sends it to the createNewFolder method to actually create the new directory
# It returns this new directory for future use
def createNewDir(soup_in):
    container = soup_in.find('h1', class_ = "material-title") # Titles are stored under this class
    new_dir_title = ''
    anchor = container.find('a')
    new_dir_title = anchor.text
    # I need to replace certain characters to match the linux directory name syntax
    # /, >, (WHITESPACE),<,|,:,&
    new_dir_title = new_dir_title.replace(' ', '_')
    new_dir_title = new_dir_title.replace('/', '_')
    new_dir_title = new_dir_title.replace('>', '_')
    new_dir_title = new_dir_title.replace('<', '_')
    new_dir_title = new_dir_title.replace('|', '_')
    new_dir_title = new_dir_title.replace(':', '_')
    new_dir_title = new_dir_title.replace('&', '_')
    return createNewFolder(new_dir_title)

# Links are either downloads, or they are just webpages, I will attempt to download and or build my own resource based on the webpages
# This is not always guaranteed success
def decideResource(link_in, new_dir_in):
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
        downloadResource(figures, new_dir_in)
    else:
        print ("No download link, now attempting to build the resource by scraping the individual page's html")
        buildResource(soup, new_dir_in)
 
# If the resource has a download link it should come to this method!
def downloadResource(figures_in, new_dir_in):
    download_link = [] # Parsed from the figure
    link_titles = [] # Parsed from figure, used to tell the file type
    for figure in figures_in:
        link_title = figure.find('a').contents[0]
        link = figure.find('a')['href']
        download_link.append(link)
        link_titles.append(link_title)
    
    print("Download link(s) found: ", download_link)
    file_type = ''
    
    for title in link_titles:
        print ("Title of the resource:", title)
        file_type = getFileType(title)
    
    for download in download_link:
        print ("Attempting to download: ", download)
        if file_type == "zip":
            downloadZIP(download, new_dir_in)
        elif file_type == "pdf":
            downloadPDF(download, link_titles[0], new_dir_in)
        else:
            print ("Unknown file type: ", file_type, " Now skipping.")
        
# If the resource is not a download, then we have to scrape the page and its html elements
def buildResource(download_in, new_dir_in):
    print("Not implemented")

# This method determines the file type by the title of the file
# I.E Somefile.pdf, this would return pdf.
def getFileType(title_in):
    return title_in[-3:].lower()
    
# Downloads the ZIP file
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
    new_dir = SAVE_PATH + title_in
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    return new_dir

# This method will extract all of the metadata we can find on a particular OER
def extractMetaData(soup_in, new_dir_in):
    final_string = ''
    final_string = new_dir_in + '\n' # The final string to save to the text file that contains the metadata
    final_string = final_string + extractMetaDetailsFirstPart(soup_in)
    final_string = final_string + extractMetaDetailsSecondPart(soup_in)
    final_string = final_string + extractMetaTags(soup_in)
    print(final_string)

# Extracts information like Subject, Grade Level, Material Type, Date Added.... etc
def extractMetaDetailsFirstPart(soup_in):
    final_string = ''
    container = soup_in.find('div', class_ = "material-details")
    abstract_anchor = container.find('dd', itemprop = "description")
    abstract_text = abstract_anchor.text
    final_string = final_string + "Details: " + abstract_text + '\n'
    
    dt_list = [] # dts are used as the headers for the meta details
    dd_list = [] # dds are used as the actual information following the headers
    
    container = soup_in.find('dl', class_ = "materials-details-first-part") # This is where the first part of the meta details are stored
    
    # No first part found
    if container is None:
        return ''
        
    dt_container = container.find_all('dt')
    dd_container = container.find_all('dd')
    
    # DT is the header. I.E. "Grade:" 
    for dt in dt_container:
        dt_list.append(dt.text)
    
    # DD is the information following the header I.E. "8th grade"
    for dd in dd_container:
        temp_dd = dd.text.strip() # Remove the white space from the front and end from each dd
        temp_dd = temp_dd.replace('\n', '') # Remove the new lines from the dd
        dd_list.append(temp_dd)
   
    # Next I will iterate through the lists to create the meta-detail string that will be saved in the file
    i = 0
    length = len(dt_list)
    while i < length:
        temp_dd = dd_list[i]
        temp_dt = dt_list[i]
        final_string = final_string + temp_dt + " " + temp_dd + "\n"
        i += 1
        
    return final_string + "\n"

# Extracts the license, language, types of media.. etc
def extractMetaDetailsSecondPart(soup_in):
    final_string = ''
    
    container = soup_in.find('div', class_ = "material-details-second-part") # This is where the first part of the meta details are stored
    
    # No second part found
    if container is None:
        return ''
        
    dt_container = container.find_all('dt')
    dd_container = container.find_all('dd')
    
    dt_list = [] # dts are used as the headers for the meta details
    dd_list = [] # dds are used as the actual information following the headers
   
   # DT is the header. I.E. "Grade:" 
    for dt in dt_container:
        dt_list.append(dt.text)
    
    # DD is the information following the header I.E. "8th grade"
    for dd in dd_container:
        temp_dd = dd.text.strip() # Remove the white space from the front and end from each dd
        temp_dd = temp_dd.replace('\n', '') # Remove the new lines from the dd
        dd_list.append(temp_dd)
   
    # Next I will iterate through the lists to create the meta-detail string that will be saved in the file
    i = 0
    length = len(dt_list)
    while i < length:
        temp_dd = dd_list[i]
        temp_dt = dt_list[i]
        final_string = final_string + temp_dt + " " + temp_dd + "\n"
        i += 1
        
    return final_string + "\n"
    
# Extracts all of the tags. I.E. Biology
def extractMetaTags(soup_in):
    final_string = 'Tags: '
    container = soup_in.find_all("li", class_ = "tag-instance keyword")
    
    # No tags found
    if container is None:
        return ''
  
    li_list = [] # This list will contain all of the tags
    
    for li in container:
        temp_li = li.text.replace('\n', '')
        temp_li = li.text.strip()
        li_list.append(temp_li)
        
    for li in li_list:
        final_string = final_string + li + '\n'
    
    return final_string

if __name__ == '__main__':
    scrape_base_page()