# LogoSimilarity# **Logo Extraction & Matching Project**

This project extracts logos from websites and groups them based on similarity.

## **Installation Guide**

### **Prerequisites**
This project requires Google Chrome to be installed on your system. If Chrome is not installed, you can install it using:

```bash
sudo apt update && sudo apt install google-chrome-stable
```

Alternatively, you can manually download it from [Google Chrome's official website](https://www.google.com/chrome/).


Before running the scripts, install the required Python modules using:

```bash
pip install pandas fastparquet selenium webdriver-manager requests beautifulsoup4 torch torchvision cairosvg tqdm scikit-learn
```

## **Execution Order**

1. **Run `extract_logos.py`**  
   This script extracts logos from websites listed in `logos.snappy.parquet` and saves the results in `logos.json`.

   ```bash
   python extract_logos.py
   ```

2. **Run `logoMatcher.py`**  
   This script reads `logos.json`, processes the logos, extracts their features, and groups similar ones.

   ```bash
   python logoMatcher.py
   ```

---

## **How It Works**
### **1. `extract_logos.py` (Extract Logos)**

- Reads a list of domains from `logos.snappy.parquet`.
- Uses `logoExtracter.py` to extract logos from each website:
  - **Checks HTML** for `<img>` tags containing "logo".
  - **Checks CSS files** for `background-image` properties containing "logo".
  - **Uses Selenium** for JavaScript-heavy websites if necessary.
- Uses multithreading to speed up the process.
- Saves extracted logos in `logos.json`.

🔹 **Success Rate: ~57%**  
Some domains fail due to:

- **Connection errors** (timeouts, inaccessible sites).
- **Weird image formats** (unsupported SVG, base64 images).
- **Logo not found** in HTML or CSS.

---

### **2. `logoMatcher.py` (Match Similar Logos)**

- Reads `logos.json` and downloads each logo.
- Converts **SVG files** to PNG for processing.
- Extracts logo features using **ResNet50** (a deep learning model for image processing).
- Uses **cosine similarity** to compare logos.
- Groups similar logos using **K-Means clustering**.
- Saves the results in `clusters_output.txt`, where each group contains similar-looking logos.

---

## **Final Output**

- `logos.json`: Extracted logos (domain → logo URL).
- `clusters_output.txt`: List of grouped domains based on logo similarity.

This system efficiently extracts and matches logos but is limited by **website availability, image format compatibility, and HTML structure inconsistencies**.

