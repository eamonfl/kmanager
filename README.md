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

![kmanager screenshot](https://github.com/user-attachments/assets/3f713dbc-cfd9-4426-ad75-665ee0f54189)

3. Command line
 Linux Kernel Management

![kmanager2 screenshot](https://github.com/user-attachments/assets/419968dc-9f7b-4899-b7c1-2a4c824fd6a5)

## Tested on

Ubuntu 24.10
Debian 12

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to enhance Kmanager.

## License
This project is licensed under the MIT License. Feel free to use, modify, and distribute it.
