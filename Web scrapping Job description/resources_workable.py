import requests
from bs4 import BeautifulSoup
import csv

base_url = "https://resources.workable.com"

# Function to scrape individual job description page
def scrape_job_page(job_url):
    try:
        response = requests.get(job_url, timeout=10)  # Increase timeout to 10 seconds
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get job title
        job_title = soup.find('h1', class_='margin-b-md').get_text(strip=True)
        
        # Find the section with requirements and skills
        requirements_section = soup.find('h2', string='Requirements and skills')
        
        if not requirements_section:
            print(f"No requirements section found for {job_url}")
            return job_title, []

        requirements_list = requirements_section.find_next('ul')
        
        if not requirements_list:
            print(f"No requirements list found for {job_url}")
            return job_title, []

        requirements = [li.get_text(strip=True) for li in requirements_list.find_all('li')]
        #print(f"{job_title} \n{requirements}\n----------------------------------------------")
        return job_title, requirements
    
    except requests.RequestException as e:
        print(f"Error fetching {job_url}: {e}")
        return None, []

# Main function to scrape the job descriptions
def main():
    try:
        url = f"{base_url}/job-descriptions/"
        #print(url)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all job links
        job_links = soup.find_all('a', class_='base-sm', href=True)
        print("open job link")
        jobs = []
        
        count = 1

        for job_link in job_links:
            job_url = job_link['href']
            #print(count)
            #count = count+1
            if not job_url.startswith('http'):
                job_url = base_url + job_url
            job_title, requirements = scrape_job_page(job_url)
            if job_title:
                jobs.append({'title': job_title, 'requirements': requirements})

        # Save results to CSV
        with open('job_descriptions.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Job Title', 'Requirements'])
            
            for job in jobs:
                writer.writerow([job['title'], '; '.join(job['requirements'])])


        # # Print the results
        # if not jobs:
        #     print("No jobs found on the main page.")
        # else:
        #     for job in jobs:
        #         print(f"Job Title: {job['title']}")
        #         print("Requirements:")
        #         for req in job['requirements']:
        #             print(f"- {req}")
        #         print("\n")
    
    except requests.RequestException as e:
        print(f"Error fetching the main page: {e}")

if __name__ == "__main__":
    main()
