from scanner import Service

# Services initializing Name, URL, ping_time seconds
p2h = Service('P2H', 'https://p2h.com/', 3)
mena = Service('MENA', 'https://google.com', 3)

# Services list for thread processing
services_list = [p2h, mena]
