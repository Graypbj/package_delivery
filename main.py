# Author: Grayson Butcher
# Student ID: 012161412
# Title: C950 WGUPS ROUTING PROGRAM

import csv
import datetime
from hashtable import HashTable
from package import Package

# Constants
TRUCK_SPEED = 18
HUB_ADDRESS = "4001 S 700 E"
CORRECTED_ADDRESS = "410 S State St"
CORRECTION_TIME = datetime.time(10, 20)

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
def load_package_data(filename="CSV/packages.csv"):
    package_hash_table = HashTable()
    try:
        with open(filename, "r", encoding="utf-8") as package_info:
            package_data = csv.reader(package_info)
            next(package_data)  # Skip the header row
            for package in package_data:
                try:
                    package_id = int(package[0])
                    package_address = package[1]
                    package_city = package[2]
                    package_state = package[3]
                    package_zip_code = package[4]
                    package_deadline = package[5]
                    package_weight = package[6]
                    notes = package[7] if len(package) > 7 else ""  # Handle missing notes

                    # Parse deadline
                    if package_deadline.upper() == "EOD":
                        deadline_time = datetime.time(17, 0)  # 5:00 PM
                    else:
                        deadline_time = datetime.datetime.strptime(package_deadline, "%I:%M %p").time()

                    # Parse notes
                    truck_restriction = None
                    delivery_group = None
                    delayed_until = None

                    if "truck 2" in notes.lower():
                        truck_restriction = "truck 2"

                    if "must be delivered with" in notes.lower():
                        # Extract package IDs from the notes
                        delivery_group_str = notes.split("with ")[1]
                        delivery_group = [pid.strip() for pid in delivery_group_str.split(",")]

                    if "delayed on flight" in notes.lower():
                        delayed_time_str = notes.split("until ")[1].strip()
                        try:
                            delayed_until = datetime.datetime.strptime(delayed_time_str, "%I:%M %p").time()
                        except ValueError:
                            print(f"Warning: Invalid delayed time format for package {package_id}: {delayed_time_str}")

                    p = Package(package_id, package_address, package_city, package_state, package_zip_code, deadline_time, package_weight, notes, delayed_until=delayed_until, truck_restriction=truck_restriction, delivery_group=delivery_group)

                    package_hash_table.set_val(package_id, p)
                except ValueError as ve:
                    print(f"Error parsing package data for package {package[0]}: {ve}")
    except FileNotFoundError:
        print(f"Error: Package file '{filename}' not found.")
    except Exception as e:
        print(f"Error: An error occurred while loading package data from '{filename}': {e}")

    return package_hash_table

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
    
    return address_to_index



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
    
    for key in package_hash_table.hash_table:
        if key is not None:
            for package_id, package in enumerate(key):
                package_data = package_hash_table.get_val(package_id)
                if package_data != "No record found":
                    if package_data.delivery_group and len(truck1) < 16:
                        if can_add_to_truck(package_data.package_id, "truck1", package_hash_table, current_time):
                            truck1.append(package_data.package_id)
    
    for key in package_hash_table.hash_table:
        if key is not None:
            for package_id, package in enumerate(key):
                package_data = package_hash_table.get_val(package_id)
                if package_data != "No record found":
                    if package_data.package_deadline != "EOD":
                        if can_add_to_truck(package_data.package_id, "truck1", package_hash_table, current_time) and len(truck1) < 16:
                            truck1.append(package_data.package_id)
    
    for key in package_hash_table.hash_table:
        if key is not None:
            for package_id, package in enumerate(key):
                package_data = package_hash_table.get_val(package_id)
                if package_data != "No record found":
                    if package_data.package_id not in truck1 and package_data.package_id not in truck2 and package_data.package_id not in truck3:
                        if can_add_to_truck(package_data.package_id, "truck1", package_hash_table, current_time) and len(truck1) < 16:
                            truck1.append(package_data.package_id)
                        elif can_add_to_truck(package_data.package_id, "truck2", package_hash_table, current_time) and len(truck2) < 16:
                            truck2.append(package_data.package_id)
                        elif can_add_to_truck(package_data.package_id, "truck3", package_hash_table, current_time) and len(truck3) < 16:
                            truck3.append(package_data.package_id)
    


# Find distance between two addresses
def dist_between(addr1, addr2):
    distance = dist_csv[addr1][addr2]
    if distance == '':
        distance = dist_csv[addr2][addr1]
    
    return float(distance)


def __main__():
    package_hash_table = HashTable()

