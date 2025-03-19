import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from logoExtracter import get_logo_url

# Load the parquet file
df = pd.read_parquet("logos.snappy.parquet", engine="fastparquet")

# Extract domain list
domains = df["domain"].tolist()

# Dictionary to store results
results = {}

def process_domain(domain):
    """Fetch logo for a domain."""
    logo_url = get_logo_url(domain)
    if logo_url:
        return domain, logo_url
    return None  # Skip if no logo found

# Use threading to process multiple domains at once
max_threads = 31  # Adjust based on your system
with ThreadPoolExecutor(max_threads) as executor:
    future_to_domain = {executor.submit(process_domain, domain): domain for domain in domains}

    for future in as_completed(future_to_domain):
        result = future.result()
        if result:
            domain, logo_url = result
            results[domain] = logo_url

# Save results to JSON file
with open("logos.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"✅ Extraction complete. Saved {len(results)} logos to logos.json")
