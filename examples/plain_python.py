from open_data_actors import run_actor

for row in run_actor("domain-intelligence-lookup", domains=["example.com"], max_items=3):
    print(row)
