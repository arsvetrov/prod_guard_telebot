from scanner import Service

# Services initializing Name, URL, ping_time seconds

service1 = Service('service1_name', 'service1_url', 60)
service2 = Service('service2_name', 'service2_url', 60)
# Your next service here


# Services list for thread processing

services_list = [service1, service2, ]  # Add your next service in list
