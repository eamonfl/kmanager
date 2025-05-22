# Kmanager

## Introduction
Kmanager is a tool to manage kernels on Debian Linux based systems. It has two modes:
-  menu
- command line

## Features
- Update to the latest available kernel from https://kernel.ubuntu.com/~kernel-ppa/mainline/
- List the latests 5 kernels(by default) from https://kernel.ubuntu.com/~kernel-ppa/mainline/
- Clear any old installed kernels
- Pull a specific kernel from https://kernel.ubuntu.com/~kernel-ppa/mainline/
- Show system version information

## Setup & Installation

1. Clone the repository:
```
bash

git clone https://github.com/eamonfl/kmanager.git
cd kamanger
```
2. Install the dependencies
```
bash

pip install -r requirements
```

## Usage
1. Run the application
```
bash

python kmanager.py
```

2. Follow the on-screen instructions:

   Linux Kernel Management

  - 1.     Update to the latest RC Kernel
  - 2.     List available RC Kernels
  - 3.     Get a specific RC Kernel
  - 4.     Cleanup. Remove old Kernels
  - 5.     Report version information
  - 6/q/e. Exit

3. Command linee
 Linux Kernel Management

options:
  -h, --help            show this help message and exit
  -u, --update           Update the Kernel
  -g GET, --get GET      Get a specific Kernel
  -c, --clean            Clean old Kernels
  -v, --version          Report Version

list options:
  -l, --list             List available Kernels
  -n NUMBER, --number NUMBER
                         Number of Kernels to List (only with -l)
## Tested on

Ubuntu 24.10
Debian 12

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to enhance Kmanager.

## License
This project is licensed under the MIT License. Feel free to use, modify, and distribute it.

