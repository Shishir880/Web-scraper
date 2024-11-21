import requests
from bs4 import BeautifulSoup
import json
import traceback
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter.ttk import Progressbar
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Function to handle retries and session management
def create_session():
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session = requests.Session()
    session.mount('https://', adapter)
    return session

# Function to scrape a webpage and return structured data
def scrape_page(url, session, update_callback, progress_callback, current_index, total_urls):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        page_data = {
            "url": url,
            "title": soup.title.string if soup.title else 'No title',
            "meta_tags": {meta.get('name', meta.get('property')): meta.get('content') for meta in soup.find_all('meta') if meta.get('content')},
            "h1": [h1.get_text() for h1 in soup.find_all('h1')],
            "h2": [h2.get_text() for h2 in soup.find_all('h2')],
            "h3": [h3.get_text() for h3 in soup.find_all('h3')],
            "h4": [h4.get_text() for h4 in soup.find_all('h4')],
            "h5": [h5.get_text() for h5 in soup.find_all('h5')],
            "paragraphs": [p.get_text() for p in soup.find_all('p')],
        }

        # Call the callback to update the GUI with the current scraping status
        update_callback(f"Scraping {url} completed...")
        progress_callback(current_index + 1, total_urls)

        return page_data

    except requests.exceptions.RequestException as e:
        update_callback(f"Request error for {url}: {e}")
        progress_callback(current_index + 1, total_urls)
        return None
    except Exception as e:
        update_callback(f"Error scraping {url}: {e}")
        print(traceback.format_exc())
        progress_callback(current_index + 1, total_urls)
        return None

# Function to scrape multiple websites
def scrape_multiple_websites(urls, output_file="scraped_data.json", update_callback=None, progress_callback=None):
    all_scraped_data = []  # List to collect data from all pages

    session = create_session()
    total_urls = len(urls)

    for idx, url in enumerate(urls):
        page_data = scrape_page(url, session, update_callback, progress_callback, idx, total_urls)
        if page_data:
            all_scraped_data.append(page_data)  # Add the page data to the list

    # Save all data to a single JSON file
    if all_scraped_data:
        with open(output_file, 'w') as f:
            json.dump(all_scraped_data, f, indent=4)
        update_callback(f"All data saved to {output_file}")

# GUI setup
def start_scraping():
    urls = url_input.get("1.0", tk.END).splitlines()
    urls = [url.strip() for url in urls if url.strip()]

    if not urls:
        messagebox.showerror("Error", "Please enter at least one URL.")
        return

    output_file = "scraped_data.json"
    text_output.delete(1.0, tk.END)  # Clear previous output
    text_output.insert(tk.END, "Scraping in progress...\n")  # Display initial message
    text_output.update()  # Refresh the output area to show the message

    progress_bar["maximum"] = len(urls)  # Set the maximum value for the progress bar
    progress_bar["value"] = 0  # Reset the progress bar to 0
    scrape_multiple_websites(urls, output_file, update_callback=update_scraping_status, progress_callback=update_progress_bar)

def stop_scraping():
    text_output.insert(tk.END, "\nScraping process stopped.\n")
    text_output.update()

def update_scraping_status(status):
    text_output.insert(tk.END, f"{status}\n", "red")
    text_output.yview(tk.END)  # Auto-scroll to the latest message

def update_progress_bar(current, total):
    progress_bar["value"] = current
    progress_bar["maximum"] = total
    progress_bar.update()

# Creating the tkinter window
window = tk.Tk()
window.title("Website Scraper")
window.geometry("400x300")  # Adjust window size

# Set black background and white text
window.configure(bg="black")

# Scraping progress area
scraping_progress_label = tk.Label(window, text="Progress:", font=("Arial", 10), bg="black", fg="white")
scraping_progress_label.pack(pady=5)

# Progress bar to show scraping progress
progress_bar = Progressbar(window, length=300, orient="horizontal", mode="determinate")
progress_bar.pack(pady=5)

# Output area for scraping progress
text_output = scrolledtext.ScrolledText(window, height=8, width=50, font=("Arial", 10), bg="black", fg="red")
text_output.pack(pady=5)

# URL input area
url_input_label = tk.Label(window, text="Enter URLs (one per line):", font=("Arial", 10), bg="black", fg="white")
url_input_label.pack(pady=5)

url_input = scrolledtext.ScrolledText(window, height=8, width=50, font=("Arial", 10), bg="black", fg="white")
url_input.pack(pady=5)

# Scraping buttons
start_button = tk.Button(window, text="Start Scraping", command=start_scraping, bg='lightblue', font=("Arial", 10))
start_button.pack(side=tk.LEFT, padx=10, pady=5)

stop_button = tk.Button(window, text="Stop Scraping", command=stop_scraping, bg='lightcoral', font=("Arial", 10))
stop_button.pack(side=tk.RIGHT, padx=10, pady=5)

# Start the GUI loop
window.mainloop()
