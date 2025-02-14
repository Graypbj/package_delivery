class Package:
    def __init__(self, package_id, package_address, package_city, package_state, package_zip, package_deadline, package_weight, package_status="at hub"):
        self.package_id = package_id
        self.package_address = package_address
        self.package_city = package_city
        self.package_state = package_state
        self.package_zip = package_zip
        self.package_deadline = package_deadline
        self.package_weight = package_weight
        self.package_status = package_status