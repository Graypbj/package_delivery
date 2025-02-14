class Package:
    def __init__(self, package_id, package_address, package_city, package_state,
                 package_zip, package_deadline, package_weight, notes="",
                 package_status="At Hub", delivery_time=None, delayed_until=None,
                 truck_restriction=None, delivery_group=None):
        self.package_id = package_id
        self.package_address = package_address
        self.package_city = package_city
        self.package_state = package_state
        self.package_zip = package_zip
        self.package_deadline = package_deadline
        self.package_weight = package_weight
        self.notes = notes
        self.package_status = package_status
        self.delivery_time = delivery_time
        self.delayed_until = delayed_until
        self.truck_restriction = truck_restriction
        self.delivery_group = delivery_group

    def __str__(self):
        return (f"Package ID: {self.package_id}, Address: {self.package_address}, "
                f"Deadline: {self.package_deadline}, Status: {self.package_status}, "
                f"Delivery Time: {self.delivery_time}, Truck Restriction: {self.truck_restriction}, "
                f"Delivery Group: {self.delivery_group}, Delayed Until: {self.delayed_until}")
