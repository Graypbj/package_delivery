# Author: Grayson Butcher
# Student ID: 012161412
# Title: C950 WGUPS ROUTING PROGRAM

import csv
import datetime
from hashtable import HashTable

# Read the distance file
with open("CSV/distances.csv") as dist:
    dist_csv = csv.reader(dist)
    dist_csv = list(dist_csv)

# Read the address file
with open("CSV/addresses.csv") as addr:
    addr_csv = csv.reader(addr)
    addr_csv = list(addr)

# Read the package file
with open("CSV/packages.csv") as pack:
    pack_csv = csv.reader(pack)
    pack_csv = list(pack)


# Create package objects from the CSV file
# After packages are objects, place them into a hash table
def load_package_data(filename, package_hash_table):
    with open(filename) as package_info:
        package_data = csv.reader(package_info)
        for package in package_data:
            package_id = int(package[0])
            package_address = package[1]
            package_city = package[2]
            package_state = package[3]
            package_zip_code = package[4]
            package_deadline = package[5]
            package_weight = package[6]
            package_status = "At Hub"

            p = package(package_id, package_address, package_city, package_state, package_zip_code, package_deadline, package_weight, package_status)

            package_hash_table.set_val(package_id, p)

def load_address_data(filename="CSV/addresses.csv"):
    address_to_index = {}
    try:
        with open(filename, "r", encoding="utf-8") as addr: # Specified encoding due to errors received
            addr_csv = csv.reader(addr)
            address_list = list(addr_csv) # Reads all rows into a list that I can iterate through

            # Check to see if the file is empty or just doesn't have any address data
            if not address_list:
                print(f"Warning: Address file '{filename} is empty.")
                return address_to_index # This will return an empty dictionary
            
            for index, row in enumerate(address_list):
                if row:
                    address = row[0].strip() # Get the address from the first column without any whitespace
                    if address:
                        address_to_index[address] = index # The address is now mapped to its index
                    else:
                        print(f"Warning: Empty Address found at row {index + 1} in '{filename}'.")
                else:
                    print(f"Warning: Empty row found at row {index + 1} in '{filename}'.")
    
    except FileNotFoundError: # Error handling for testing
        print(f"Error: Address file '{filename}' not found.")
    except Exception as e:
        print(f"Error: An error occurred while loading address data from '{filename}': {e}")

def get_address_index(address, address_data):
    if address in address_data:
        return address_data[address]
    else:
        print(f"Warning: Address '{address}' not found in address data.")
        return None

def update_package_address(package_id, new_address, package_hash_table):
    package = package_hash_table.get_val(package_id) # Get the desired package to update

    if package != "No record found":
        package.package_address = new_address # Update the address
        package_hash_table.set_val(package_id, package) # Update the address within the hash table
        print(f"Package {package_id} address has been updated to: {new_address}")
    else:
        print(f"Warning: Package {package_id} not found in hash table.")

def assign_packages_to_trucks(package_hash_table, truck1, truck2, truck3, current_time):
    # Make sure trucks are "empty"
    truck1.clear()
    truck2.clear()
    truck3.clear()

    # Check if package can be added to truck (is it at the hub or delayed?)
    def can_add_to_truck(package_id, truck, package_hash_table, current_time):
        package = package_hash_table.get_val(package_id)
        if package == "No record found":
            return False # The package does not exist
        if package.package_id in truck1 and truck != truck1:
            return False
        if package.package_id in truck2 and truck != truck2:
            return False
        if package.package_id in truck3 and truck != truck3:
            return False
        
        # Check if it is a delayed package
        if package.delayed_until:
            combined = datetime.datetime.combine(datetime.date.today(), current_time)
            delayed_time = datetime.datetime.combine(datetime.date.today(), package.delayed_until)
            if combined < delayed_time:
                return False

        return True
    


# Find distance between two addresses
def dist_between(addr1, addr2):
    distance = dist_csv[addr1][addr2]
    if distance == '':
        distance = dist_csv[addr2][addr1]
    
    return float(distance)


def __main__():
    package_hash_table = HashTable()

