# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 00:47:21 2026

@author: acscw
"""

"""
Bayt.com Job Scraper (Updated Skills Extraction)
"""

import json
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class BaytScraper:
    
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = None
        self.jobs_data = []
    
    # ================= DRIVER =================
    def start_driver(self):
        self.driver = webdriver.Chrome(options=self.options)
        print("WebDriver started")
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()
            print("WebDriver closed")
    
    # ================= UTILS =================
    def random_delay(self, min_sec=1, max_sec=3):
        time.sleep(random.uniform(min_sec, max_sec))
    
    def scroll_page(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.random_delay(0.5, 1)

    def deep_scroll(self):
        """Scroll متكرر لتحميل المحتوى الكسول"""

        last_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )

        for _ in range(6):

            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            time.sleep(random.uniform(1.5, 2.5))

            new_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

            if new_height == last_height:
                break

            last_height = new_height
    
    def clean_text(self, text):
        if not text:
            return None
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip() if text.strip() else None
    
    def safe_extract(self, xpath):
        try:
            return self.driver.find_element(By.XPATH, xpath).text.strip()
        except:
            return None


    # ================= LINKS =================
    def extract_job_links(self, listing_url, max_pages=1):
        job_links = []
        
        for page in range(1, max_pages + 1):
            url = f"{listing_url}?page={page}" if page > 1 else listing_url
            print(f"Page {page}: {url}")
            
            self.driver.get(url)
            self.random_delay(2, 4)
            self.scroll_page()
            
            links = self.driver.find_elements(By.XPATH, "//li[@data-js-job]//a[@data-js-aid='jobID']")

            for link in links:
                href = link.get_attribute("href")
                if href and "/jobs/" in href:
                    job_links.append(href)
            
            print(f"Found {len(links)} jobs")
        
        job_links = list(dict.fromkeys(job_links))
        print(f"Total: {len(job_links)} jobs")
        return job_links
    

    # ================= SKILLS (UPDATED) =================
    def extract_skills(self):
    
        skills = []
    
        try:
            headers = self.driver.find_elements(
                By.XPATH,
                "//h2[@class='h5' and ("
                "normalize-space(text())='Skills' "
                "or normalize-space(text())='المهارات'"
                ")]"
            )
    
            for header in headers:
    
                
                containers = header.find_elements(
                    By.XPATH,
                    "following-sibling::*[1] | following-sibling::div[1]"
                )
    
                for container in containers:
    
                    temp = []
    
                    # 1) li
                    lis = container.find_elements(By.TAG_NAME, "li")
                    for li in lis:
                        t = li.text.strip()
                        if 3 < len(t) < 300:
                            temp.append(t)
    
                    # 2) p
                    ps = container.find_elements(By.TAG_NAME, "p")
                    for p in ps:
                        t = p.text.strip()
                        if 5 < len(t) < 300:
                            temp.append(t)
    
                    # 3) direct_text
                    direct_text = container.text.strip()
                    if direct_text and len(direct_text) < 500:
                        lines = direct_text.split("\n")
    
                        for line in lines:
                            l = line.strip()
                            if 5 < len(l) < 300:
                                temp.append(l)
    
                    # Cleaning
                    temp = list(dict.fromkeys(temp))
    
                    if temp:
                        skills = temp
                        break
    
                if skills:
                    break
    
        except Exception as e:
            print("Skills error:", e)
    
        if skills:
            return ", ".join(skills)
    
        return None



    # ================= JOB DETAILS =================
    def extract_job_details(self, job_url):
        print(f"Extracting: {job_url}")
        
        try:
            self.driver.get(job_url)
            self.random_delay(2, 3)
            self.deep_scroll()
            
            # ========== JOB TITLE ==========
            job_title = self.clean_text(self.safe_extract("//h1[@id='job_title']"))
            
            # ========== COMPANY ==========
            company = self.clean_text(self.safe_extract(
                "//ul[contains(@class, 'media-list')]//*[contains(@class, 't-bold')]"
            ))
            
            if not company:
                company = "Confidential Company"

            # ========== LOCATION ==========
            location_parts = []

            location_elements = self.driver.find_elements(By.XPATH, 
                "//ul[contains(@class, 'media-list')]//span[contains(@class, 't-mute')]/a[contains(@class, 't-mute')]"
            )

            for elem in location_elements:
                text = elem.text.strip()
                if text:
                    location_parts.append(text)

            location = ", ".join(location_parts) if location_parts else None
            
            # ========== JOB TYPE ==========
            job_type = self.safe_extract(
                "//div[@data-automation-id='id_type_level_experience']//span[contains(@class, 'u-stretch')]"
            )

            if job_type:
                job_type = job_type.split("·")[0].strip() if "·" in job_type else job_type

            job_type = self.clean_text(job_type)
            
            # ========== DESCRIPTION ==========
            description = self.clean_text(self.safe_extract(
                "//h2[text()='Job description']/following-sibling::div[contains(@class, 't-break')]"
            ))
            
            # ========== SKILLS ==========
            skills = self.extract_skills()
            
            job_data = {
                "Job_Title": job_title,
                "Company": company,
                "Location": location,
                "Job_Type": job_type,
                "Description": description,
                "Skills": skills,
                "Job_URL": job_url
            }
            
            print(f"{job_title} | Skills: {'Found' if skills else 'Not Found'}")
            return job_data
            
        except Exception as e:
            print(f"Error: {e}")
            return None
    

    # ================= MAIN SCRAPER =================
    def scrape_jobs(self, listing_url, max_pages=1, output_file="bayt_jobs.json"):
        try:
            self.start_driver()
            
            job_links = self.extract_job_links(listing_url, max_pages)
            
            for i, job_url in enumerate(job_links, 1):
                print(f"\n[{i}/{len(job_links)}]")
                
                job_data = self.extract_job_details(job_url)
                
                if job_data:
                    self.jobs_data.append(job_data)
                    self.save_to_json(output_file)
                
                if i < len(job_links):
                    self.random_delay(1, 3)
            
            print(f"\n Done! {len(self.jobs_data)} jobs saved to {output_file}")
            
        finally:
            self.close_driver()
    

    def save_to_json(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.jobs_data, f, ensure_ascii=False, indent=2)


# ==================== RUN ====================
if __name__ == "__main__":

    
    scraper = BaytScraper(headless=False)
    
    scraper.scrape_jobs(
        listing_url="https://www.bayt.com/en/saudi-arabia/jobs/",
        max_pages=1,
        output_file="bayt_jobs--.json"
    )
