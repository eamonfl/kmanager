import requests
import platform
from bs4 import BeautifulSoup
import subprocess
import os
from urllib.parse import urljoin

def list(val):
  """ make a request to the main kernel page"""
  url = "https://kernel.ubuntu.com/~kernel-ppa/mainline/"
  hrefs=[]
  try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            """ We onlt want the HREFs from the links, these will contain the kernel versions available"""
            for link in links:
                hrefs.append(link.get('href'))
        else:
            print("Failed to fetch the page. Status code:", response.status_code)
        """get the current running kernel"""
        plat=platform.release()
        #
        # Check if an RC kernel strip accordingly
        if 'rc' in plat:
          plat=f'{plat[:3]}-{plat[12:15]}'
        else:
          plat=f'{plat[:3]}'
        """ Now print all the hrefs. Strip the first char(an 'v') and the last char(a '/') ) """
        for href in hrefs[-5:]:
            #print(href[1:-1])
            if plat == href[1:-1]:
              status='(Valid **Running**)'
            else:
               statusurl=url + href + 'amd64/status'
               status=get_kernel_status(statusurl)
            print(f'{href[1:-1]:7} \t{status}')

  except requests.RequestException as e:
            print("Error:", e)
  return
#####################
def update(val):
    #
    # We can call the system script uktools-upgrade with the -r arg to do the upgrade
    sudo='sudo'
    tool='/usr/sbin/uktools-upgrade'
    arg='-r'

    subprocess.call([sudo,tool,arg])
    #
    # Now reset the terminal, the script can leave the terminal in a non-echo state
    tool='stty'
    arg='sane'
    subprocess.call([tool,arg])

    return
#############################
def clean(val):
    #
    # Cannot get 'dpkg' to run as a subprocess so giving up for the moment.
    # Call a bash script instead
    print('Cleaning Up')
    sudo='sudo'
    tool='/usr/local/bin/kclean.sh'
    subprocess.call([sudo,tool],shell=False)

    return
#############################
def get(val):
    #
    # Get the requested kernel files
    url = f'https://kernel.ubuntu.com/~kernel-ppa/mainline/v{val[0]}/amd64/'  # Replace with the actual website URL
    extension = '.deb'  # Change this to the desired extension
    output_path = '/var/tmp'

    download_files_with_ext(url, extension, output_path)

    print('Download complete!')
    return
#############################
def get_kernel_status(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)       
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the content of the file
            if int(response.text) == 0:
                status='(Valid)'
            else:
                status='(Invalid)'
            return status
        else:
            print(f"Failed to fetch file. Status code: {response.status_code}")
            return '(Invalid)'
    except Exception as e:
        print(f"An error occurred: {e}")
        return '(Invalid)'
##############################
def download_files_with_ext(url, extension, output_path):
  """Downloads all files with the given extension from the URL and saves them to the output path.

  Args:
    url: The URL of the website.
    extension: The extension of the files to download (e.g., ".pdf", ".jpg").
    output_path: The directory where the downloaded files will be saved.
  """

  # Create the output directory if it doesn't exist
  os.makedirs(output_path, exist_ok=True)

  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')

  # Find all links on the webpage
  links = soup.find_all('a')

  # Extract URLs for files with the specified extension
  file_urls = [urljoin(url, link['href']) for link in links if link['href'].endswith(extension)]

  # Download each file
  for i, file_url in enumerate(file_urls):
    filename = file_url.split('/')[-1]
    file_path = os.path.join(output_path, filename)

    print(f'Downloading file {i+1}/{len(file_urls)}: {filename} to {output_path}')

    # Download the file in chunks to improve efficiency
    try:
      response = requests.get(file_url, stream=True)
      if response.status_code == 200:
        with open(file_path, 'wb') as f:
          for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
              f.write(chunk)
      else:
        print(f'Failed to download {filename}, error code: {response.status_code}')
    except Exception as err:
      print(f'Error downloading {filename}: {err}')

