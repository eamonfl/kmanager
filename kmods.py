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
    """
    Manages kernel operations such as listing, downloading, updating, and cleaning kernels.

    This class encapsulates various attributes and methods to interact with the
    Ubuntu kernel PPA, retrieve kernel information, manage local kernel files,
    and provide system information.

    Attributes:
        platform (str): The current kernel release string (e.g., '5.15.0-78-generic').
        kernel_url (str): Base URL for the Ubuntu mainline kernel PPA.
        kernel_arch (str): The system's processor architecture (e.g., 'x86_64', 'aarch64').
        system (str): The operating system type (e.g., 'Linux').
        distro_name (str): The distribution name (e.g., 'Ubuntu').
        distro_version (str): The distribution version (e.g., '22.04').
        listnumber (int): The number of latest kernels to list by default.
        availablekernels (list): A list to store available kernel version strings.
    """
    #
    def __init__(self):
        """
        Initializes the Kops instance with system-specific information.

        Sets attributes like the current platform's kernel release, the URL for
        the kernel PPA, system architecture, OS type, distribution name/version,
        and initializes `listnumber` and `availablekernels`.
        """
        self.platform=platform.release() # Stores the current kernel release (e.g., '5.15.0-78-generic')
        self.kernel_url='https://kernel.ubuntu.com/~kernel-ppa/mainline/' # Base URL for Ubuntu mainline kernels
        self.kernel_arch=platform.processor() # Stores system architecture (e.g., 'x86_64', 'aarch64'). Note: PPA interactions (get, list status) currently use 'amd64' in URLs.
        self.system=platform.system() # Stores the OS type (e.g., 'Linux')
        self.distro_name=distro.name() # Stores the distribution name (e.g., 'Ubuntu')
        self.distro_version=distro.version() # Stores the distribution version (e.g., '22.04')
        self.listnumber=5 # Default number of kernels to list
        self.availablekernels=[] # Stores a list of available kernel version strings fetched from the PPA

    #####################
    def clean(self,val):
        """
        Cleans old kernel files from the system by calling an external script.

        This method executes '/usr/local/bin/kclean.sh' with sudo privileges
        to remove old kernel packages. The `val` argument is not currently used.
        """
        # The original attempt to use 'dpkg' directly via subprocess was problematic,
        # possibly due to complexities in managing interactive prompts or privileges.
        # Calling an external shell script simplifies this by encapsulating the dpkg logic.
        print('Cleaning Up')
        sudo='sudo'
        tool='/usr/local/bin/kclean.sh'
        return_code = subprocess.call([sudo,tool],shell=False)
        if return_code != 0:
            print(f"Error: The kernel cleanup script (kclean.sh) failed with exit code {return_code}.")

    #####################
    def version(self,val):
        """
        Displays the version of the kupdate application and system information.

        Prints the application version, OS type, distribution name and version,
        current kernel release, and hostname. The `val` argument is not used.
        """
        print(f'\n\033[1mkupdate v0.2a \nsysinfo:\n- {self.system} ({self.distro_name}\
               {self.distro_version}) \n- {self.platform}\n- {platform.uname().node}\033[0m \n')

    #####################
    def list(self,val):
        """
        Lists available kernels from the Ubuntu mainline PPA.

        Fetches the list of kernel versions from `self.kernel_url`.
        It then filters and displays the latest `self.listnumber` kernel versions.
        For each version, it checks its status (e.g., if it's the currently
        running one or if it's a valid downloadable build for amd64).
        The `val` argument is not used directly by this method for its primary logic,
        though it's passed from a context where it might exist (CLI parsing).
        The number of kernels to list is controlled by `self.listnumber`.
        """
        hrefs=[]
        try:
            response = requests.get(self.kernel_url, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            # Parse the HTML content of the kernel PPA page using BeautifulSoup.
            # 'html.parser' is the built-in Python HTML parser.
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all '<a>' (anchor) tags, which typically contain links.
            links = soup.find_all('a')
            # Extract the 'href' attribute from each link.
            # These hrefs usually represent directories for kernel versions.
            for link in links:
                # Filter for hrefs that likely represent kernel version directories.
                # Kernel version directories on the PPA typically start with 'v'.
                # This also helps ignore other links like 'Parent Directory'.
                if 'v' in link.get('href'):
                    hrefs.append(link.get('href'))
            # Extract major.minor-rcN from the currently running kernel string for comparison.
            plat=__extract_version_info__(self.platform)
            # Iterate through the N most recent kernel versions found (controlled by self.listnumber).
            # hrefs are typically sorted chronologically on the PPA page, so the end of the list is newer.
            for href in hrefs[-self.listnumber:]:
                # Store the cleaned version string (e.g., "6.5.3-rc1") in availablekernels.
                # href has a leading 'v' and a trailing '/', which are stripped.
                kernel_version_str = href[1:-1]
                self.availablekernels.append(kernel_version_str)
                # Determine the status of this kernel version.
                if plat == kernel_version_str:
                    # If the listed kernel matches the running kernel version.
                    status='(Valid **Running**)'
                else:
                    # For other kernels, check their build status for 'amd64' architecture.
                    # Construct the URL to the 'status' file for this kernel version.
                    statusurl=self.kernel_url + href + 'amd64/status' # URL to check status for amd64 architecture.
                    status=self.__get_kernel_status__(statusurl)
                print(f'{kernel_version_str:7} \t{status}')

        except requests.exceptions.ConnectionError as e:
            print(f"Error: Connection failed for {self.kernel_url}. Please check your network connection. Details: {e}")
        except requests.exceptions.Timeout as e:
            print(f"Error: Request timed out for {self.kernel_url}. The server might be too slow. Details: {e}")
        except requests.exceptions.HTTPError as e:
            print(f"Error: HTTP error occurred for {self.kernel_url}. Status code: {e.response.status_code}. Details: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error: An unexpected error occurred while fetching {self.kernel_url}. Details: {e}")
    #####################
    def update(self,val):
        """
        Updates the system to the latest available valid kernel from the PPA.

        This method first calls `self.list(1)` to determine the most recent
        kernel version. It compares this with the currently running kernel.
        If an update is available and the latest kernel is marked as 'Valid',
        it prompts the user for confirmation to download and install.
        If the kernel files have been previously downloaded to '/var/tmp/',
        it uses those; otherwise, it calls `self.get()` to download them.
        Finally, it attempts a dry-run of `dpkg -i` for the downloaded .deb files.
        The `val` argument is not used.
        """

        # Use StringIO to capture the output of self.list(1) in memory.
        # redirect_stdout temporarily changes the standard output to the StringIO buffer.
        new_out = StringIO()
        with redirect_stdout(new_out):
            # Call self.list(1) to get information about the very latest kernel.
            # The output, including its status, will be captured in new_out.
            self.list(1)

        # Retrieve the captured output.
        ver=new_out.getvalue()
        # The captured output format is "X.Y.Z-rcN (Status)". Split to get the status part.
        vers=ver.split(' ')
        # Get the version string of the currently running kernel.
        running=__extract_version_info__(self.platform)
        # Get the version string of the latest available kernel from the populated list.
        availablekernel=self.availablekernels[-1]

        # Compare running kernel with the latest available one.
        if running == availablekernel:
            print(f'No update required, lastest version is already installed({running})')
            return

        # Check if the latest available kernel is marked as 'Valid'.
        # vers[-1] contains the status string, e.g., "(Valid)\n".
        if 'Valid' not in vers[-1]:
            # If not valid (e.g., build failed for amd64), do not proceed.
            print(f'No valid downloadable version for {availablekernel}')
            return

        print(f'Update required from {running} to {availablekernel}')
        
        # Prompt the user for confirmation before proceeding with download/install.
        prompt = input("Do you want to continue? (yes/no): ").strip().lower()
        if prompt not in {"yes", "y"}:
            # If user declines, provide manual installation instructions.
            # The kernel version fragment is used to generalize the .deb file names.
            print(f'To manually install the new kernel run:\n'
                f'sudo dpkg -i /var/tmp/*{availablekernel.split("-")[1]}*.deb')
            return

        # Extract a fragment of the kernel version string (typically the part after major.minor-).
        # This fragment (e.g., "060503rc1") is used to identify related .deb files.
        kernel_version_fragment = availablekernel.split('-')[1]
        # Check if .deb files for this kernel version fragment already exist in /var/tmp/.
        installs = list(Path("/var/tmp/").glob(f"*{kernel_version_fragment}*.deb"))

        if installs:
            # If files exist, inform the user they've already been downloaded.
            print(f'Version {availablekernel} has already been downloaded.')
        else:
            # If files don't exist, call self.get() to download them.
            self.get([availablekernel])
            print(f'Version {availablekernel} has been downloaded.')
            # Refresh the list of .deb files after download.
            installs = list(Path("/var/tmp/").glob(f"*{kernel_version_fragment}*.deb"))

        # Prepare and execute the dpkg command for a dry run to simulate installation.
        # This shows what would happen without actually installing.
        command = ["sudo", "dpkg", "-i", "--dry-run"] + installs
        return_code = subprocess.call(command, shell=False)
        if return_code != 0:
            print(f"Error: 'dpkg --dry-run' command failed with exit code {return_code}. The kernel installation was not simulated successfully.")
        return

    #############################
    def get(self,val):
        """
        Downloads kernel .deb files for a specific version.

        Constructs the URL for the specified kernel version (from `val[0]`)
        and architecture (amd64), then calls `__download_files_with_ext__`
        to download all .deb files from that URL to '/var/tmp/'.

        Args:
            val (list): A list where `val[0]` is a string representing the
                        kernel version to download (e.g., "6.5.3").
        """

        # Construct the specific URL for the kernel version and architecture.
        # val[0] contains the kernel version string like "6.5.3".
        # Example URL: https://kernel.ubuntu.com/~kernel-ppa/mainline/v6.5.3/amd64/
        url = f'https://kernel.ubuntu.com/~kernel-ppa/mainline/v{val[0]}/amd64/' # URL for amd64 architecture kernels.
        extension = '.deb'  # We are interested in .deb packages.
        output_path = '/var/tmp' # Standard temporary directory for downloads.

        self.__download_files_with_ext__(url, extension, output_path)

        print('Download complete!')
    #############################
    def __get_kernel_status__(self,url):
        """
        Checks the status of a kernel version by trying to access its 'status' file.

        Sends a GET request to the provided URL, which should point to a
        'status' file for a specific kernel build (e.g., on the Ubuntu kernel PPA,
        this indicates if a build for amd64 was successful).

        Args:
            url (str): The URL of the 'status' file to check.

        Returns:
            str: '(Valid)' if the URL returns a 200 status code,
                 '(Invalid)' if it returns a 404 status code or an exception occurs.
        """
        try:
            # Send a GET request to the kernel status URL.
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            # If request is successful (e.g. status 200), it's a valid build.
            return '(Valid)'
        except requests.exceptions.HTTPError as e:
            # Specifically handle 404 Not Found as an 'Invalid' build status.
            if e.response.status_code == 404:
                return '(Invalid)'
            # For other HTTP errors, print a message and return Invalid.
            print(f"Error: HTTP error occurred while checking status for {url}. Status code: {e.response.status_code}. Details: {e}")
            return '(Invalid)'
        except requests.exceptions.ConnectionError as e:
            print(f"Error: Connection failed while checking status for {url}. Please check your network connection. Details: {e}")
            return '(Invalid)'
        except requests.exceptions.Timeout as e:
            print(f"Error: Request timed out while checking status for {url}. The server might be too slow. Details: {e}")
            return '(Invalid)'
        except requests.exceptions.RequestException as e:
            print(f"Error: An unexpected error occurred while checking status for {url}. Details: {e}")
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

        # Ensure the target directory for downloads exists; create it if not.
        # exist_ok=True means it won't raise an error if the directory already exists.
        os.makedirs(output_path, exist_ok=True)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            # Parse the HTML content of the specific kernel version page.
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all '<a>' (anchor) tags on the page.
            links = soup.find_all('a')

            # Create a list of full URLs for files that end with the specified extension (e.g., '.deb').
            # urljoin ensures that relative links (like 'linux-headers-...deb') are correctly combined with the base URL.
            file_urls = [urljoin(url, link['href']) \
                        for link in links if link['href'].endswith(extension)]

            # Iterate through the list of identified file URLs to download each one.
            for i, file_url in enumerate(file_urls):
                # Extract the filename from the URL.
                filename = file_url.split('/')[-1]
                # Construct the full local path to save the file.
                file_path = os.path.join(output_path, filename)

                print(f'Downloading file {i+1}/{len(file_urls)}: {filename} to {output_path}')

                # Download the file using streaming to handle potentially large files efficiently.
                # stream=True defers downloading the response body until content is accessed.
                try:
                    response_file = requests.get(file_url, stream=True, timeout=10)
                    response_file.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                    # Open the local file in write-binary mode.
                    with open(file_path, 'wb') as f:
                        # Iterate over the response data in chunks of 1024 bytes.
                        for chunk in response_file.iter_content(chunk_size=1024):
                            if chunk:  # Filter out keep-alive new chunks (which are empty).
                                f.write(chunk) # Write the current chunk to the file.
                except requests.exceptions.ConnectionError as e_file:
                    print(f"Error: Connection failed for {file_url} while downloading. Please check your network connection. Details: {e_file}")
                except requests.exceptions.Timeout as e_file:
                    print(f"Error: Request timed out for {file_url} while downloading. The server might be too slow. Details: {e_file}")
                except requests.exceptions.HTTPError as e_file:
                    print(f"Error: HTTP error occurred for {file_url} while downloading. Status code: {e_file.response.status_code}. Details: {e_file}")
                except requests.exceptions.RequestException as e_file:
                    print(f"Error: An unexpected error occurred while downloading {file_url}. Details: {e_file}")
        except requests.exceptions.ConnectionError as e:
            print(f"Error: Connection failed for {url} (kernel branch page). Please check your network connection. Details: {e}")
        except requests.exceptions.Timeout as e:
            print(f"Error: Request timed out for {url} (kernel branch page). The server might be too slow. Details: {e}")
        except requests.exceptions.HTTPError as e:
            # Handle case where the kernel branch URL itself gives an HTTP error (e.g., 404 for a non-existent version)
            print(f"Error: HTTP error occurred for {url} (kernel branch page). Status code: {e.response.status_code}. Details: {e}")
            print(f'\n****Failed to find kernel branch:  {url}****\n') # Keep original specific error message
        except requests.exceptions.RequestException as e:
            print(f"Error: An unexpected error occurred while fetching {url} (kernel branch page). Details: {e}")

def __extract_version_info__(version_string):
    """
    Extracts the major.minor version and release candidate (RC) information
    from a kernel version string.

    The function uses a regular expression to parse standard kernel version formats.
    For example, "6.14.0-061400rc3-generic" would yield "6.14-rc3".
    If no RC is present, like "5.15.0-78-generic", it returns "5.15".
    It can handle versions with or without patch numbers and build metadata if they
    follow the typical `major.minor[.patch][-buildmetadata][rcX]` structure.

    Args:
        version_string (str): The kernel version string to parse.
            Expected formats include:
            - "X.Y.Z-aabbccRCN-generic" (e.g., "6.14.0-061400rc3-generic")
            - "X.Y.Z-generic" (e.g., "5.15.0-generic")
            - "X.Y-rcN" (e.g., "6.8-rc1", common in PPA folder names)
            - "X.Y" (e.g., "6.5")

    Returns:
        str or None:
            - If an RC number is found, returns a string in the format "major.minor-rcN"
              (e.g., "6.14-rc3").
            - If no RC number is found but major.minor is matched, returns "major.minor"
              (e.g., "5.15").
            - Returns None if the `version_string` does not match the expected pattern
              to extract major.minor version.
    """
    # Regex explanation:
    # (\d+\.\d+)       : Captures the 'major.minor' part (e.g., "6.14") into group 1. This is required.
    # (?:\.\d+)?       : Optionally matches (but doesn't capture) a patch version (e.g., ".0"). The '?:' makes it non-capturing.
    # (?:-\d+)?        : Optionally matches (but doesn't capture) build metadata or other numbers like "-061400".
    # (?:rc(\d+))?     : Optionally matches (but doesn't capture the "rc" part itself) "rc" followed by one or more digits.
    #                   The digits (\d+) following "rc" are captured into group 2 (e.g., "3" from "rc3").
    match = re.match(r"(\d+\.\d+)(?:\.\d+)?(?:-\d+)?(?:rc(\d+))?", version_string)

    major_minor=None # Initialize to None, in case of no match.
    if match:
        # Group 1 will always be the major.minor version if a match occurs.
        major_minor = match.group(1)
        # Group 2 is the RC number string (e.g., "3") or None if no "rc" part was matched.
        rc_number_str = match.group(2)
        if rc_number_str:
            # If an RC number string exists, convert it to an integer.
            rc_number = int(rc_number_str)
            # Append "-rcN" to the major.minor string.
            major_minor=f"{major_minor}-rc{rc_number}"

    # Returns the "major.minor" string, optionally with "-rcN" appended, or None if no match.
    return major_minor
