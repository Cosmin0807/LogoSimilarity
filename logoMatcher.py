import torch
import torchvision.transforms as transforms
from torchvision import models
import numpy as np
import requests
from io import BytesIO
import json
from tqdm import tqdm
from PIL import Image
import cairosvg
import io
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from torchvision.models import ResNet50_Weights

# Load ResNet model
model = models.resnet50(weights=ResNet50_Weights.DEFAULT)
model.eval()  # Set to evaluation mode

# Define image preprocessing transformations
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load JSON file containing logos
json_file = "logos.json"  # Replace with your file
with open(json_file, "r") as f:
    logos_data = json.load(f)

# Function to extract features directly from a URL
def extract_features_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP failures

        img_format = url.split(".")[-1].lower()

        if img_format == "svg":
            # Convert SVG to PNG bytes
            png_bytes = cairosvg.svg2png(bytestring=response.content)
            img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
        else:
            img = Image.open(BytesIO(response.content)).convert("RGB")

        img_tensor = transform(img).unsqueeze(0)  # Add batch dimension

        with torch.no_grad():
            features = model(img_tensor)  # Extract features
        
        return features.squeeze().numpy()  # Convert to NumPy array
    except Exception as e:
        print(f"Failed to process {url}: {e}")
        return None

# Store extracted features
logo_features = {}
for domain, logo_url in tqdm(logos_data.items(), desc="Extracting features"):
    features = extract_features_from_url(logo_url)
    if features is not None:
        logo_features[domain] = features

# Convert features to NumPy arrays for similarity calculation
logo_list = list(logo_features.keys())  # List of domains
feature_matrix = np.array(list(logo_features.values()))  # Stack features
similarity_matrix = cosine_similarity(feature_matrix)

# Function to find similar logos
n_clusters = 100
kmeans = KMeans(n_clusters=n_clusters, random_state=0)
labels = kmeans.fit_predict(feature_matrix)

# Group logos by cluster
clusters = {}
for label, domain in zip(labels, logo_list):
    if label not in clusters:
        clusters[label] = []
    clusters[label].append(domain)

output_file = "clusters_output.txt"
with open(output_file, "w") as f:
    for label, group in clusters.items():
        f.write(f"Group {label}:\n")
        for domain in group:
            f.write(f"    {domain}\n")
        f.write("\n")

print(f"Clusters have been saved to {output_file}.")
