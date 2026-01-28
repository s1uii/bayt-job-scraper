# Bayt Jobs Scraper

A Python Selenium-based scraper that collects job listings from Bayt.com and exports structured data to JSON.

## Features
- Scrapes job listings from multiple pages
- Extracts job title, company, location, job type, description, and skills
- Supports Arabic and English job posts
- Handles dynamic content using scrolling and delays
- Saves results incrementally to JSON

## Requirements
- Python 3.9+
- Google Chrome
- ChromeDriver (compatible with your Chrome version)

## Installation

Run the following command:

    pip install -r requirements.txt

## Usage

Run the scraper:

    python bayt_scraper.py

Main parameters inside the script:
- listing_url: Bayt job listings page
- max_pages: Number of pages to scrape
- headless: Set to False to reduce blocking

## Output
Data is saved in bayt_jobs.json with the following fields:
- Job_Title
- Company
- Location
- Job_Type
- Description
- Skills
- Job_URL

## Notes
- Use reasonable delays to avoid being blocked.
- This project is for educational purposes only.
