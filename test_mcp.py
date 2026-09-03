import logistics_mcp

print("=== MCP TOOL TESTS ===")

print("\n--- check_stock: valid ---")
print(logistics_mcp.check_stock("amoxicillin"))

print("\n--- check_stock: valid ---")
print(logistics_mcp.check_stock("paracetamol"))

print("\n--- DELIVERY ROUTE ---")
print(logistics_mcp.plan_delivery_route("Vihiga Health Post"))

print("\n--- Distance (Km) ---")
print(logistics_mcp.distance_km(
    logistics_mcp.CLINICS[0],
    logistics_mcp.CLINICS[1]
))

print("\n--- Delivery ETA ---")
print(logistics_mcp.get_delivery_eta("Kisii Family Clinic","Homa Bay Lakeside Clinic"))