#!/usr/bin/env python
"""kmenu helps provide and optionally update the current installed Linux Kernel"""
import sys
import os
import argparse
from colorama import init, Fore, Back, Style
import kmods

# Initialize colorama
init(autoreset=True)

def clear_screen():
    """Clear the screen using ANSI escape sequences"""
    print("\033[H\033[J", end="")

def parse_args():
    """Create and parse command line arguments"""
    xparser = argparse.ArgumentParser(description=f"{Fore.BLUE}{Style.BRIGHT}\
                                      Linux Kernel Management{Style.RESET_ALL}")
    parser = xparser.add_mutually_exclusive_group()

    # Define arguments with colored help messages
    parser.add_argument("-u", "--update", action="store_true", help=f"{Fore.GREEN}\
                        Update the Kernel{Style.RESET_ALL}")
    # For the list command with optional number parameter
    list_group = xparser.add_argument_group('list options')
    list_group.add_argument("-l", "--list", action="store_true", help=f"{Fore.GREEN}\
                        List available Kernels{Style.RESET_ALL}")
    list_group.add_argument("-n", "--number", type=int, default=5, help=f"{Fore.GREEN}\
                        Number of Kernels to List (only with -l){Style.RESET_ALL}")
    parser.add_argument("-g", "--get", type=str, nargs=1, help=f"{Fore.GREEN}\
                        Get a specific Kernel{Style.RESET_ALL}")
    parser.add_argument("-c", "--clean", action="store_true", help=f"{Fore.GREEN}\
                        Clean old Kernels{Style.RESET_ALL}")
    parser.add_argument("-v", "--version", action="store_true", help=f"{Fore.GREEN}\
                        Report Version{Style.RESET_ALL}")

    return xparser.parse_args()

def menu():
    """Displays a colorful menu and gets user input."""
    # Menu items with colors
    menu_items = [
        f"{Fore.GREEN}1.{Style.RESET_ALL}     Update to the latest RC Kernel",
        f"{Fore.GREEN}2.{Style.RESET_ALL}     List available RC Kernels",
        f"{Fore.GREEN}3.{Style.RESET_ALL}     Get a specific RC Kernel",
        f"{Fore.GREEN}4.{Style.RESET_ALL}     Cleanup. Remove old Kernels",
        f"{Fore.GREEN}5.{Style.RESET_ALL}     Report version information",
        f"{Fore.RED}6/q/e.{Style.RESET_ALL} Exit"
    ]

    # Display menu header
    print(f"\n{Fore.YELLOW}{Back.BLUE}{Style.BRIGHT} Linux Kernel Management {Style.RESET_ALL}\n")

    # Display menu items
    for item in menu_items:
        print(f"  {item}")

    # Get user input
    while True:
        try:
            choice = input(f"\n{Fore.CYAN}Enter your choice (1-6/q/e):{Style.RESET_ALL} ")
            if choice in ('1', '2', '3', '4', '5', '6', 'q', 'e'):
                if choice == 'q' or choice == 'e': choice = '6'
                return int(choice)
            print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 6.\
                  {Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Operation cancelled by user.{Style.RESET_ALL}")
            return 6  # Exit on Ctrl+C

def is_debian_based_file_check():
    return os.path.exists('/etc/debian_version')

def main():
    """Main program execution"""
    # First parse command line arguments
    arguments = parse_args()
    cli = vars(arguments)
    # Incase we are using the '--list' extract the optional '--number'
    kops.listnumber = arguments.number

    # Check for command line arguments
    for key, val in cli.items():
        if val is True or isinstance(val, list):
            func = getattr(kops, key)
            func(val)
            sys.exit(0)

    # Main loop for the menu system
    while True:
        try:
            clear_screen()
            choice = menu()

            if choice == 1:
                print(f"\n{Fore.CYAN}Updating to the latest RC Kernel...{Style.RESET_ALL}")
                kops.update(val)
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

            elif choice == 2:
                print(f"\n{Fore.CYAN}Listing available RC Kernels...{Style.RESET_ALL}")
                kops.list(val)
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

            elif choice == 3:
                print(f"\n{Fore.CYAN}Getting a specific RC Kernel...{Style.RESET_ALL}")
                version = input(f"{Fore.YELLOW}Enter the kernel version to get:{Style.RESET_ALL}  ")
                kops.get([version])
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

            elif choice == 4:
                print(f"\n{Fore.CYAN}Cleaning up old Kernels...{Style.RESET_ALL}")
                kops.clean(val)
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

            elif choice == 5:
                print(f"\n{Fore.CYAN}Displaying version information...{Style.RESET_ALL}")
                kops.version(val)
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

            elif choice == 6 or choice == 'q' or choice == 'e':
                print(f"\n{Fore.RED}Exiting...{Style.RESET_ALL}")
                break

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Operation cancelled by user.{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    # Ony run if its a Debian based system
    if not is_debian_based_file_check():
        print("This system is not Debian-based system....exiting....")
        sys.exit(1)
    
    kops = kmods.Kops()
    main()
