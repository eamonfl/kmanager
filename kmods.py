""" This Class defintion is used by kupdate """
import platform
import re
import subprocess
from pathlib import Path
import os
from io import StringIO  # Python 3
from contextlib import redirect_stdout
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

import distro

class Kops:
    """ build a class to hold various data required for get kernels"""
    #
    def __init__(self):
        self.platform=platform.release()
        self.kernel_url='https://kernel.ubuntu.com/~kernel-ppa/mainline/'
        self.kernel_arch=platform.processor()
        self.system=platform.system()
        self.distro_name=distro.name()
        self.distro_version=distro.version()
        self.listnumber=5
        self.availablekernels=[]

    #####################
    def clean(self,val):
        """Clean the old kernel files from the system"""
        #
        # Cannot get 'dpkg' to run as a subprocess so giving up for the moment.
        # Call a bash script instead
        print('Cleaning Up')
        sudo='sudo'
        tool='/usr/local/bin/kclean.sh'
        subprocess.call([sudo,tool],shell=False)

    #####################
    def version(self,val):
        """ return version number of the app """
        print(f'\n\033[1mkupdate v0.2a \nsysinfo:\n- {self.system} ({self.distro_name}\
               {self.distro_version}) \n- {self.platform}\n- {platform.uname().node}\033[0m \n')

    #####################
    def list(self,val):
        """ make a request to the main kernel page"""
        hrefs=[]
        try:
            response = requests.get(self.kernel_url,timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a')
                # We only want the HREFs from the links
                # these will contain the kernel versions available
                for link in links:
                    #
                    # Occassional a file is created in the kernels folder, ignore it.
                    # Just look for files starting with a 'v'
                    if 'v' in link.get('href'):
                        hrefs.append(link.get('href'))
            else:
                print("Failed to fetch the page. Status code:", response.status_code)
            #get the current running kernel
            plat=__extract_version_info__(self.platform)
            # Now print all the hrefs.
            # Strip the first char(an 'v') and the last char(a '/') )
            for href in hrefs[-self.listnumber:]:
                self.availablekernels.append(href[1:-1])
                if plat == href[1:-1]:
                    status='(Valid **Running**)'
                else:
                    statusurl=self.kernel_url + href + 'amd64/status'
                    status=self.__get_kernel_status__(statusurl)
                print(f'{href[1:-1]:7} \t{status}')

        except requests.RequestException as e:
            print("Error:", e)
    #####################
    def update(self,val):
        """ We can call self.list to generate the last kernel from kernel.ubuntu.com. Then
        we can check if it is already installed"""

        # Create the in-memory "file"
        new_out = StringIO()
        with redirect_stdout(new_out):
            #
            # Get the last available kernel
            self.list(1)

        #if 'Running' in new_out.getvalue():
        ver=new_out.getvalue()
        vers=ver.split(' ')
        running=__extract_version_info__(self.platform)
        availablekernel=self.availablekernels[-1]
        if running == availablekernel:
            print(f'No update required, lastest version is already installed({running})')
            return
        if 'Valid' in vers[-1]:
            # Now we need to extract the kernel to get from kernel.ubuntu.com
            print(f'Update required from{running} to {availablekernel}')
            #
            # Now install if required
            prompt = input("Do you want to continue? (yes/no): ")
            if prompt.lower() in ["yes", "y"]:
                ## Just extract the 'rc' piece of the kernel to install
                installs=list(Path("/var/tmp/").glob(f"*{availablekernel.split('-')[1]}*.deb"))
                if installs:
                    ## Files are already in /var/tmp, no need to redownload
                    print(f'Version {availablekernel} has already been downloaded.')
                else:
                    #
                    # Download the .deb files
                    self.get([availablekernel])
                    print(f' Version {availablekernel} has been downloaded.')
                command = ["sudo", "dpkg", "-i","--dry-run"] + installs
                subprocess.call(command,shell=False)
            else:
                print(f'To manually install the new kernel run: \
                sudo dpkg -i /var/tmp/*{availablekernel.split('-')[1]}*.deb"')
        else:
            # Version found but invalid
            print(f'No valid downloadable version for {availablekernel}')
    #############################
    def get(self,val):
        """ Get the requested kernel files. Replace with the actual website URL """

        url = f'https://kernel.ubuntu.com/~kernel-ppa/mainline/v{val[0]}/amd64/'
        extension = '.deb'  # Change this to the desired extension
        output_path = '/var/tmp'

        self.__download_files_with_ext__(url, extension, output_path)

        print('Download complete!')
    #############################
    def __get_kernel_status__(self,url):
        """ Check to see if the kernel works on this architecture """
        try:
            # Send a GET request to the URL
            response = requests.get(url,timeout=10)
            # Check if the request was successful (status code 200)
            status='(Valid)'
            if response.status_code == 404:
                status='(Invalid)'
            return status
        except Exception as e:
            print(f"An error occurred: {e}")
            return '(Invalid)'
    ##############################
    def __download_files_with_ext__(self,url, extension, output_path):
        """Downloads all files with the given extension from the URL
        and saves them to the output path.

        Args:
          url: The URL of the website.
          extension: The extension of the files to download (e.g., ".pdf", ".jpg").
          output_path: The directory where the downloaded files will be saved.
        """

        # Create the output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        response = requests.get(url,timeout=10)
        if response.status_code != 200:
            print(f'\n****Failed to find kernel branch:  {url}****\n')
        else:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links on the webpage
            links = soup.find_all('a')

            # Extract URLs for files with the specified extension
            file_urls = [urljoin(url, link['href']) \
                        for link in links if link['href'].endswith(extension)]

            # Download each file
            for i, file_url in enumerate(file_urls):
                filename = file_url.split('/')[-1]
                file_path = os.path.join(output_path, filename)

                print(f'Downloading file {i+1}/{len(file_urls)}: {filename} to {output_path}')

                # Download the file in chunks to improve efficiency
                try:
                    response = requests.get(file_url, stream=True,timeout=10)
                    if response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=1024):
                                if chunk:  # filter out keep-alive new chunks
                                    f.write(chunk)
                    else:
                        print(f'Failed to download {filename}, error code: {response.status_code}')
                except Exception as err:
                    print(f'Error downloading {filename}: {err}')
def __extract_version_info__(version_string):
    """
    Extracts the major.minor version and the release candidate number from a version string.

    Args:
        version_string: The version string (e.g., "6.14.0-061400rc3-generic").

    Returns:
        A string containing the major.minor version and the rc number (e.g., "6.14-rc3"),
        or just the major.minor version (e.g., "6.14") if no rc number is present,
        or None if the version string doesn't match the expected pattern.
    """
    match = re.match(r"(\d+\.\d+)(?:\.\d+)?(?:-\d+)?(?:rc(\d+))?", version_string)

    major_minor=None
    if match:
        major_minor = match.group(1)
        rc_number_str = match.group(2)
        if rc_number_str:
            rc_number = int(rc_number_str)
            #return f"{major_minor}-rc{rc_number}"  # Include "-rc"
            major_minor=f"{major_minor}-rc{rc_number}"  # Include "-rc"

    return major_minor  # Return just major.minor, major.minor plus rc or None rc
