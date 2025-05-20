import sys
import argparse
from bs4 import BeautifulSoup
import kmods

def menu():
  """Displays the menu and gets user input."""
  print("\n1. Update to the latest RC Kernel")
  print("2. List available RC Kernels")
  print("3. Get a specific RC Kernel")
  print("4. Cleanup. Remove old Kernels")
  print("5. Exit\n")
  while True:
    choice = input("Enter your choice (1/2/3/4/5): ")
    if choice in ('1', '2', '3', '4', '5'):
      return int(choice)
    else:
      print("Invalid choice. Please enter 1, 2, 3, 4 or 5.")
def update():
  return

def get():
  return

def args():
  # Create an ArgumentParser object
  xparser = argparse.ArgumentParser(description="Linux Kernel Management")
  parser=xparser.add_mutually_exclusive_group()

  # Define arguments with options, types, and help messages
  parser.add_argument("-u", "--update", action="store_true", help="Update the Kernel")
  parser.add_argument("-l", "--list", action="store_true", help="List available Kernels")
  parser.add_argument("-g", "--get", type=str, nargs=1, help="Get a specific Kernel")
  parser.add_argument("-c", "--clean", action="store_true", help="Clean old Kernels")

  # Parse arguments
  arguments = xparser.parse_args()

  # Only one argument on the command line is allowed, exit if sys.argv is greater than 2
  #if len(sys.argv) > 2:
  #   print('Too Many arguments, only one CLI argument allowed..')
  #   sys.exit(1)
  #
  # If we have a cli arg which one ? In the cli dict one of the values will be True
  #cli={update:arguments.update,list:arguments.list,get:arguments.get,clean:arguments.clean}
  cli=[]
  cli=vars(arguments)
  #
  #Check for a true value if so we can use the key to call the relevant function. Also check if we are using get('-g') as it
  #needs a kernel version number after it
  for key, val in cli.items():
    if val == True or isinstance(val,list) == True :
      func = getattr(kmods, key)
      func(val)
      sys.exit(0)
  
  return

def main():
  """Check for arguments passed on he command line"""
  args()
  """Main loop for the menu system."""
  while True:
    choice = menu()
    if choice == 1:
      #  Update to the latest RC Kernel
      print("You selected to Update to the latest RC Kernel")
      kmods.update(None)
    elif choice == 2:
      # List available RC Kernels
      print("You selected to List available RC Kernels")
      kmods.list(None)
    elif choice == 3:
      # Get a specific RC Kernel
      print("You selected to Get a specific RC Kernel")
      version=input("Enter the kernel version to get:  ")
      kmods.get([version])
    elif choice == 4:
      # Cleanup. Remove old Kernels
      print("You selected to Cleanup. Remove old Kernels")
      kmods.clean(None)
    elif choice == 5:
      print("Exiting...")
      break

if __name__ == "__main__":
  main()
