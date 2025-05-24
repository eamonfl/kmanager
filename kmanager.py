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
    """Clears the terminal screen using ANSI escape sequences.

    This function prints the ANSI escape codes for clearing the screen and
    moving the cursor to the home position.
    """
    print("\033[H\033[J", end="")

def parse_args():
    """Creates and parses command-line arguments using argparse.

    Defines arguments for updating the kernel, listing available kernels,
    getting a specific kernel, cleaning old kernels, and reporting the version.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """
    xparser = argparse.ArgumentParser(description=f"{Fore.BLUE}{Style.BRIGHT}\
                                      Linux Kernel Management{Style.RESET_ALL}")
    # Ensures that only one of the arguments in this group can be present on the command line.
    # For example, you can't update and clean at the same time via CLI.
    parser = xparser.add_mutually_exclusive_group()

    # Define arguments with colored help messages
    # These are the main operations, mutually exclusive.
    parser.add_argument("-u", "--update", action="store_true", help=f"{Fore.GREEN}\
                        Update the Kernel{Style.RESET_ALL}")
    # The '-l' and '-n' arguments are grouped for listing kernels.
    # '-n' is only meaningful if '-l' is also present.
    # However, argparse itself doesn't enforce that '-n' requires '-l' here,
    # this logic is handled implicitly by how 'listnumber' is used in main().
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
    """Displays a colorful interactive menu and captures user input.

    The menu provides options for various kernel management tasks such as
    updating, listing, getting specific versions, cleaning old kernels,
    and displaying version information.

    Returns:
        int: The user's menu choice as an integer (1-6).
             Returns 6 if the user chooses to exit or cancels via Ctrl+C.
    """
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
            # Validate if the input is one of the allowed menu options or exit characters
            if choice in ('1', '2', '3', '4', '5', '6', 'q', 'e'):
                # Map 'q', 'e', or '6' to the integer 6 for consistent exit handling
                if choice in ('q','e','6'):
                    choice='6'
                return int(choice) # Return the valid choice as an integer
            # If input is invalid, inform the user and loop again
            print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 6.\
                  {Style.RESET_ALL}")
        except KeyboardInterrupt: # Handle Ctrl+C gracefully
            print(f"\n{Fore.RED}Operation cancelled by user.{Style.RESET_ALL}")
            return 6  # Treat Ctrl+C as an exit choice

def is_debian_based_file_check():
    """Checks if the system is Debian-based by looking for the /etc/debian_version file.

    Returns:
        bool: True if /etc/debian_version exists, False otherwise.
    """
    return os.path.exists('/etc/debian_version')

def main():
    """Main program execution flow.

    This function orchestrates the kernel management tool. It first checks if
    the system is Debian-based. If not, it exits.
    It then parses command-line arguments. If arguments are provided, it executes
    the corresponding kernel operation and exits.
    If no command-line arguments are given, it enters an interactive menu loop,
    allowing the user to choose various kernel management tasks.
    """
    # First parse command line arguments
    arguments = parse_args()
    cli = vars(arguments)
    # Incase we are using the '--list' extract the optional '--number'
    kops.listnumber = arguments.number

    # Process command-line arguments.
    # If any relevant CLI argument is found (e.g. -u, -l, -g, -c, -v),
    # the corresponding function in kops is called and the program exits.
    # This loop iterates through parsed arguments. 'key' is the arg name (e.g., 'update'),
    # and 'val' is its value (True if an action flag, list for args like -g).
    for key, val in cli.items():
        if val is True or isinstance(val, list): # Check if the argument was passed
            func = getattr(kops, key) # Dynamically get the method from kops object
            func(val) # Call the method
            sys.exit(0) # Exit after CLI operation is done

    # Main interactive loop for the menu system.
    # This loop runs if no command-line arguments were processed.
    while True:

            clear_screen()
            choice = str(menu()) # Display menu and get user's choice

            # Match the user's choice to the corresponding action.
            match choice:
                case '1':
                    print(f"\n{Fore.CYAN}Updating to the latest RC Kernel...{Style.RESET_ALL}")
                    # Pass None as 'val' is not relevant for menu-driven actions.
                    kops.update(None)
                    # Pauses execution until the user presses Enter, allowing them to read the output.
                    input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

                case '2':
                    print(f"\n{Fore.CYAN}Listing available RC Kernels...{Style.RESET_ALL}")
                    # Pass None as 'val' is not relevant for menu-driven actions.
                    kops.list(None)
                    input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

                case '3':
                    print(f"\n{Fore.CYAN}Getting a specific RC Kernel...{Style.RESET_ALL}")
                    version = input(f"{Fore.YELLOW}Enter the kernel version to get:{Style.RESET_ALL}  ")
                    kops.get([version])
                    input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

                case '4':
                    print(f"\n{Fore.CYAN}Cleaning up old Kernels...{Style.RESET_ALL}")
                    # Pass None as 'val' is not relevant for menu-driven actions.
                    kops.clean(None)
                    input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

                case '5':
                    print(f"\n{Fore.CYAN}Displaying version information...{Style.RESET_ALL}")
                    # Pass None as 'val' is not relevant for menu-driven actions.
                    kops.version(None)
                    input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

                case 'q' | 'e' | '6':  # Handles exit conditions
                    print(f"\n{Fore.RED}Exiting....{Style.RESET_ALL}")
                    break # Exit the main loop

                case _:  # Default case for invalid menu input
                    print(f"\n{Fore.RED}Invalid choice! Try again.{Style.RESET_ALL}")
                    # Pauses for user to acknowledge the error message.
                    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    # Perform an initial check to ensure the script is run on a Debian-based system.
    # Exits if the system is not Debian-based, as the tool relies on Debian-specific commands/structures.
    if not is_debian_based_file_check():
        print("This system is not Debian-based system....exiting....")
        sys.exit(1)

    kops = kmods.Kops()
    main()
