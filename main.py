# Author: Grayson Butcher
# Student ID: 012161412
# Title: C950 WGUPS ROUTING PROGRAM


import csv
import datetime
from package import Package
from hashtable import HashTable

# Constants
TRUCK_SPEED = 18
HUB_ADDRESS = "4001 S 700 E"
CORRECTED_ADDRESS = "410 S State St"
CORRECTION_TIME = datetime.time(10, 20)
START_TIME = datetime.time(8, 0)  # All trucks depart at 8:00 AM

# Load addresses from addresses.csv
def load_address_data(filename="CSV/addresses.csv"):
    address_to_index = {}
    try:
        with open(filename, "r", encoding="utf-8") as addr:
            addr_csv = csv.reader(addr)
            address_list = list(addr_csv)
            if not address_list:
                print(f"Warning: Address file '{filename}' is empty.")
                return address_to_index
            for index, row in enumerate(address_list):
                if row:
                    address = row[0].strip()
                    if address:
                        address_to_index[address] = index
                    else:
                        print(f"Warning: Empty address found at row {index + 1} in '{filename}'.")
                else:
                    print(f"Warning: Empty row found at row {index + 1} in '{filename}'.")
    except FileNotFoundError:
        print(f"Error: Address file '{filename}' not found.")
    except Exception as e:
        print(f"Error: An error occurred while loading address data from '{filename}': {e}")
    return address_to_index

# Load package data from packages.csv
def load_package_data(filename="CSV/packages.csv"):
    package_hash_table = HashTable()
    try:
        with open(filename, "r", encoding="utf-8") as package_info:
            package_data = csv.reader(package_info)
            next(package_data)  # Skip header row
            for package in package_data:
                try:
                    package_id = int(package[0])
                    package_address = package[1]
                    package_city = package[2]
                    package_state = package[3]
                    package_zip = package[4]
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
                        delivery_group_str = notes.split("with ")[1]
                        delivery_group = [pid.strip() for pid in delivery_group_str.split(",")]
                    if "delayed on flight" in notes.lower():
                        delayed_time_str = notes.split("until ")[1].strip()
                        try:
                            delayed_until = datetime.datetime.strptime(delayed_time_str, "%I:%M %p").time()
                        except ValueError:
                            print(f"Warning: Invalid delayed time format for package {package_id}: {delayed_time_str}")

                    p = Package(package_id, package_address, package_city, package_state, package_zip,
                                    deadline_time, package_weight, notes, package_status="At Hub",
                                    delivery_time=None, delayed_until=delayed_until,
                                    truck_restriction=truck_restriction, delivery_group=delivery_group)
                    package_hash_table.set_val(package_id, p)
                except ValueError as ve:
                    print(f"Error parsing package data for package {package[0]}: {ve}")
    except FileNotFoundError:
        print(f"Error: Package file '{filename}' not found.")
    except Exception as e:
        print(f"Error: An error occurred while loading package data from '{filename}': {e}")
    return package_hash_table

# Load distance data from distances.csv
def load_distance_data(filename="CSV/distances.csv"):
    distance_matrix = []
    try:
        with open(filename, "r", encoding="utf-8") as dist:
            dist_csv = csv.reader(dist)
            distance_matrix = list(dist_csv)
            for i in range(len(distance_matrix)):
                for j in range(len(distance_matrix[i])):
                    if distance_matrix[i][j] == '':
                        distance_matrix[i][j] = 0.0
                    else:
                        try:
                            distance_matrix[i][j] = float(distance_matrix[i][j])
                        except ValueError:
                            print(f"Warning: Invalid distance value at row {i + 1}, column {j + 1}")
                            distance_matrix[i][j] = 0.0
    except FileNotFoundError:
        print(f"Error: Distance file '{filename}' not found.")
    except Exception as e:
        print(f"Error: An error occurred while loading distance data from '{filename}': {e}")
    return distance_matrix

# Based on the address string, this will find the index of the address in the distances file. This doesn't return the distances, only the index.
def get_address_index(address, address_data):
    # Attempt exact match first
    if address in address_data:
        return address_data[address]
    # Attempt a correction: replace "Station" with "Sta" if needed because of package 9. I don't know why the data is this way but I figured I needed to code it to adjust for that.
    corrected = address.replace("Station", "Sta")
    if corrected in address_data:
        return address_data[corrected]
    print(f"Warning: Address '{address}' not found in address data.")
    return None

# This function updates package 9's address but can update any package if needed.
def update_package_address(package_id, new_address, package_hash_table):
    package = package_hash_table.get_val(package_id)
    if package != "No record found":
        package.package_address = new_address
        package_hash_table.set_val(package_id, package)
        print(f"Package {package_id} address has been updated to: {new_address}")
    else:
        print(f"Warning: Package {package_id} not found in hash table.")

# Based on restrictions, delivery time, and delays, this function assigns all packages to a truck.
def assign_packages_to_trucks(package_hash_table, truck1, truck2, truck3, current_time):
    truck1.clear()
    truck2.clear()
    truck3.clear()

    def can_add_to_truck(package, current_time):
        if not isinstance(package, Package):
            return False
        if package.delayed_until:
            combined = datetime.datetime.combine(datetime.date.today(), current_time)
            delayed_time = datetime.datetime.combine(datetime.date.today(), package.delayed_until)
            if combined < delayed_time:
                return False
        return True

    # Assign packages with truck restrictions to truck 2.
    for bucket in package_hash_table.hash_table:
        for package_id, _ in bucket:
            package = package_hash_table.get_val(package_id)
            if (package != "No record found"
                    and package.truck_restriction == "truck 2"
                    and can_add_to_truck(package, current_time)
                    and len(truck2) < 16):
                truck2.append(package.package_id)
                package.truck_id = 2

    # Assign packages that must be delivered together.
    for bucket in package_hash_table.hash_table:
        for package_id, _ in bucket:
            package = package_hash_table.get_val(package_id)
            if (package != "No record found"
                    and package.delivery_group
                    and can_add_to_truck(package, current_time)
                    and len(truck1) < 16):
                for dep_package_id in package.delivery_group:
                    dep_package = package_hash_table.get_val(dep_package_id)
                    if (dep_package != "No record found"
                            and can_add_to_truck(dep_package, current_time)
                            and len(truck1) < 16):
                        truck1.append(dep_package.package_id)
                        dep_package.truck_id = 1

    # Assign packages with deadlines to truck 1
    for bucket in package_hash_table.hash_table:
        for package_id, _ in bucket:
            package = package_hash_table.get_val(package_id)
            if (package != "No record found"
                    and package.package_deadline != datetime.time(17, 0)
                    and can_add_to_truck(package, current_time)
                    and len(truck1) < 16):
                truck1.append(package.package_id)
                package.truck_id = 1

    # Fill remaining capacity of trucks
    for bucket in package_hash_table.hash_table:
        for package_id, _ in bucket:
            package = package_hash_table.get_val(package_id)
            if (package != "No record found"
                    and package.package_id not in truck1
                    and package.package_id not in truck2
                    and package.package_id not in truck3):
                if can_add_to_truck(package, current_time) and len(truck1) < 16:
                    truck1.append(package.package_id)
                    package.truck_id = 1
                elif can_add_to_truck(package, current_time) and len(truck2) < 16:
                    truck2.append(package.package_id)
                    package.truck_id = 2
                elif can_add_to_truck(package, current_time) and len(truck3) < 16:
                    truck3.append(package.package_id)
                    package.truck_id = 3

# This function uses the address indexes found above to find the distance between two destinations
def dist_between(addr1_index, addr2_index, dist_csv):
    if addr1_index is None or addr2_index is None:
        return float('inf')
    if 0 <= addr1_index < len(dist_csv) and 0 <= addr2_index < len(dist_csv[0]):
        distance = dist_csv[addr1_index][addr2_index]
        if distance == '':
            distance = dist_csv[addr2_index][addr1_index]
        return float(distance)
    else:
        print(f"Warning: Index out of range: addr1_index={addr1_index}, addr2_index={addr2_index}")
        return float('inf')

# This is my implimentation of the nearest neighbor algorithm
def nearest_neighbor_algorithm(truck_packages, address_data, package_hash_table, dist_csv, start_address_index):
    route = [start_address_index]
    unvisited_packages = set(truck_packages)
    current_location_index = start_address_index

    while unvisited_packages:
        nearest_location = None
        min_distance = float('inf')
        nearest_package = None

        for package_id in list(unvisited_packages):
            package = package_hash_table.get_val(package_id)
            if package == "No record found":
                continue
            address = package.package_address
            location_index = get_address_index(address, address_data)
            if location_index is None:
                continue
            distance = dist_between(current_location_index, location_index, dist_csv)
            if distance < min_distance:
                min_distance = distance
                nearest_location = location_index
                nearest_package = package_id

        if nearest_location is not None:
            route.append(nearest_location)
            unvisited_packages.remove(nearest_package)
            current_location_index = nearest_location
        else:
            break

    route.append(start_address_index)
    return route

# This function simulates the delivery of all of the packages for a single truck
def deliver_packages(route, truck_id, package_hash_table, address_data, dist_csv, current_time, total_mileage):
    updated_time = current_time
    updated_mileage = total_mileage
    delivered_packages = set()

    for i in range(len(route) - 1):
        from_location_index = route[i]
        to_location_index = route[i + 1]

        distance = dist_between(from_location_index, to_location_index, dist_csv)
        travel_time = datetime.timedelta(hours=distance / TRUCK_SPEED)
        updated_datetime = datetime.datetime.combine(datetime.date.today(), updated_time) + travel_time
        updated_time = updated_datetime.time()
        updated_mileage += distance

        # Deliver packages at the destination.
        for bucket in package_hash_table.hash_table:
            for package_id, _ in bucket:
                package = package_hash_table.get_val(package_id)
                if package != "No record found" and package_id not in delivered_packages:
                    address = package.package_address
                    location_index = get_address_index(address, address_data)
                    if location_index == to_location_index:
                        package.package_status = "Delivered"
                        package.delivery_time = updated_time
                        package_hash_table.set_val(package.package_id, package)
                        print(f"Truck {truck_id}: Delivered package {package.package_id} to {address} at {updated_time}")
                        delivered_packages.add(package_id)
    return updated_time, updated_mileage

# This function shows where a package is at based on a given time.
def get_package_status(package_id, package_hash_table, query_time):
    package = package_hash_table.get_val(package_id)
    if package == "No record found":
        return "Package not found"

    original_address = "300 State St" # Original address of package 9
    display_address = package.package_address
    if package_id == 9:
        if query_time >= CORRECTION_TIME:
            display_address = CORRECTED_ADDRESS
        else:
            display_address = original_address

    print(f"\nPackage ID: {package.package_id}")
    print(f"Delivery Address: {display_address}") # Use display_address here
    print(f"Delivery Deadline: {package.package_deadline}")
    print(f"Delivery City: {package.package_city}")
    print(f"Delivery ZIP Code: {package.package_zip}") # Changed to package.package_zip
    print(f"Package Weight: {package.package_weight} lbs")

    if package.package_status == "Delivered" and package.delivery_time is not None:
        delivered_dt = datetime.datetime.combine(datetime.date.today(), package.delivery_time)
        query_dt = datetime.datetime.combine(datetime.date.today(), query_time)
        if delivered_dt <= query_dt:
            return f"Delivered at {package.delivery_time}"
        else:
            return f"En Route on Truck {package.truck_id}" if package.truck_id else "En Route"
    return f"En Route on Truck {package.truck_id}" if query_time >= START_TIME else "At Hub"

# This function simply tells you where the truck is and its current packages based on a given time
def display_truck_status(truck_id, truck_packages, package_hash_table, query_time):
    print(f"\nStatus for Truck {truck_id} at {query_time}:")
    for package_id in sorted(truck_packages):
        status = get_package_status(package_id, package_hash_table, query_time)
        print(f"  Package {package_id}: {status}")

# This function adds the mileage to the truck to make sure that all of the miles are correct at a given time
def simulate_truck_mileage(truck_route, start_time, query_time, dist_csv):
    current_dt = datetime.datetime.combine(datetime.date.today(), start_time)
    query_dt = datetime.datetime.combine(datetime.date.today(), query_time)
    total_mileage = 0.0

    for i in range(len(truck_route) - 1):
        from_idx = truck_route[i]
        to_idx = truck_route[i+1]
        distance = dist_between(from_idx, to_idx, dist_csv)
        travel_time = datetime.timedelta(hours=distance / TRUCK_SPEED)
        if current_dt + travel_time <= query_dt:
            total_mileage += distance
            current_dt += travel_time
        else:
            remaining = query_dt - current_dt
            hours = remaining.total_seconds() / 3600.0
            total_mileage += TRUCK_SPEED * hours
            return total_mileage
    return total_mileage

# This function calls the simulate truck mileage and display truck status functions to show where each truck is at a given time
def display_all_trucks_status(truck1, truck2, truck3, package_hash_table, query_time,
                                     truck_route1, truck_route2, truck_route3, start_time, truck_3_start, dist_csv):
    print("\n--- Truck Status Snapshot ---")
    mileage1 = simulate_truck_mileage(truck_route1, start_time, query_time, dist_csv)
    print(f"\nTruck 1 mileage up to {query_time}: {mileage1:.2f} miles")
    display_truck_status(1, truck1, package_hash_table, query_time)

    mileage2 = simulate_truck_mileage(truck_route2, start_time, query_time, dist_csv)
    print(f"\nTruck 2 mileage up to {query_time}: {mileage2:.2f} miles")
    display_truck_status(2, truck2, package_hash_table, query_time)

    mileage3 = simulate_truck_mileage(truck_route3, truck_3_start, query_time, dist_csv)
    print(f"\nTruck 3 mileage up to {query_time}: {mileage3:.2f} miles")
    display_truck_status(3, truck3, package_hash_table, query_time)

    print(f"Total mileage for all trucks: {(mileage1 + mileage2 + mileage3):.2f}")

# This is the user interface which enables the user to interact with the exposed functions
def user_interface(package_hash_table, address_data, dist_csv, total_mileage,
                                     truck1, truck2, truck3, truck_route1, truck_route2, truck_route3, start_time, truck_3_start):
    while True:
        print("\nWGUPS Routing Program")
        print("1. View package status at a specific time")
        print("2. View truck status at a specific time (one truck)")
        print("3. View total mileage (end-of-day)")
        print("4. View ALL trucks' statuses and mileage at a specific time")
        print("5. Dispaly truck status at End-of-Day")
        print("6. Exit")

        choice = input("Enter your selection: ")

        if choice == "1":
            try:
                package_id = int(input("Enter the package ID: "))
                time_str = input("Enter the time (HH:MM AM/PM): ")
                query_time = datetime.datetime.strptime(time_str, "%I:%M %p").time()
                status = get_package_status(package_id, package_hash_table, query_time)
                print(f"\nPackage {package_id} status at {query_time}: {status}")
            except ValueError:
                print("Invalid input. Please enter a valid package ID and time.")

        elif choice == "2":
            try:
                truck_id = int(input("Enter truck ID (1, 2, or 3): "))
                time_str = input("Enter the time (HH:MM AM/PM): ")
                query_time = datetime.datetime.strptime(time_str, "%I:%M %p").time()
                if truck_id == 1:
                    display_truck_status(truck_id, truck1, package_hash_table, query_time)
                elif truck_id == 2:
                    display_truck_status(truck_id, truck2, package_hash_table, query_time)
                elif truck_id == 3:
                    display_truck_status(truck_id, truck3, package_hash_table, query_time)
                else:
                    print("Invalid truck ID")
            except ValueError:
                print("Invalid input. Please enter a valid truck ID and time.")

        elif choice == "3":
            print(f"\nTotal mileage traveled by all trucks (end-of-day): {total_mileage:.2f} miles")

        elif choice == "4":
            try:
                time_str = input("Enter the time (HH:MM AM/PM): ")
                query_time = datetime.datetime.strptime(time_str, "%I:%M %p").time()
                display_all_trucks_status(truck1, truck2, truck3, package_hash_table, query_time,
                                                 truck_route1, truck_route2, truck_route3, start_time, dist_csv)
            except ValueError:
                print("Invalid time format. Please try again.")
        
        elif choice == "5":
            display_all_trucks_status(truck1, truck2, truck3, package_hash_table, datetime.time(17,0), truck_route1, truck_route2, truck_route3, start_time, truck_3_start, dist_csv)

        elif choice == "6":
            break
        else:
            print("Invalid choice. Please enter a valid option.")

def main():
    address_data = load_address_data()
    package_hash_table = load_package_data()
    dist_csv = load_distance_data()

    truck1, truck2, truck3 = [], [], []
    current_time = START_TIME
    total_mileage = 0.0

    # 1 Assign packages to trucks
    assign_packages_to_trucks(package_hash_table, truck1, truck2, truck3, current_time)

    # 2 Get hub index
    hub_index = get_address_index(HUB_ADDRESS, address_data)
    if hub_index is None:
        print("Error: Hub address not found in address data.")
        return

    # 3 Update package 9's address
    if current_time <= CORRECTION_TIME:
        update_package_address(9, CORRECTED_ADDRESS, package_hash_table)

    # 4 Build routes for each truck
    truck_route1 = nearest_neighbor_algorithm(truck1, address_data, package_hash_table, dist_csv, hub_index)
    truck_route2 = nearest_neighbor_algorithm(truck2, address_data, package_hash_table, dist_csv, hub_index)
    truck_route3 = nearest_neighbor_algorithm(truck3, address_data, package_hash_table, dist_csv, hub_index)

    # 5 Deliver packages (simulate full route)
    """for truck_id in range(1, 4):
        updated_time, updated_mileage = deliver_packages(
            {1: truck_route1, 2: truck_route2, 3: truck_route3}[truck_id],
            truck_id,
            package_hash_table,
            address_data,
            dist_csv,
            current_time,
            total_mileage
        )
        current_time = updated_time
        total_mileage = updated_mileage """
    
    updated_time1, updated_mileage = deliver_packages(truck_route1, 1, package_hash_table, address_data, dist_csv, START_TIME, total_mileage)
    total_mileage = updated_mileage

    updated_time2, updated_mileage = deliver_packages(truck_route2, 2, package_hash_table, address_data, dist_csv, START_TIME, total_mileage)
    total_mileage = updated_mileage

    truck_3_start = min(updated_time1, updated_time2)
    updated_time, updated_mileage = deliver_packages(truck_route3, 3, package_hash_table, address_data, dist_csv, truck_3_start, total_mileage)
    total_mileage = updated_mileage
    print(total_mileage)

    # 6 Start the user interface
    user_interface(package_hash_table, address_data, dist_csv, total_mileage,
                                     truck1, truck2, truck3, truck_route1, truck_route2, truck_route3, START_TIME, truck_3_start)

if __name__ == "__main__":
    main()
