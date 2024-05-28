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
        return job_title, requirements
    
    except requests.RequestException as e:
        print(f"Error fetching {job_url}: {e}")
        return None, []

# Main function to scrape the job descriptions
def main():
    try:
        url = f"{base_url}/job-descriptions/"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Containers for job links and departments
        jobs = []
        current_department = None

        # Iterate over all elements
        for element in soup.find_all(['h5', 'a']):
            if element.name == 'h5':  # This is a department heading
                current_department = element.get_text(strip=True)
            elif element.name == 'a' and current_department:  # This is a job link under the current department
                if 'base-sm' in element.get('class', []):  # Only process <a> tags with the 'base-sm' class
                    job_url = element['href']
                    if not job_url.startswith('http'):
                        job_url = base_url + job_url
                    job_title, requirements = scrape_job_page(job_url)
                    if job_title:
                        # print(current_department)
                        # print(job_title)
                        # print(requirements)
                        #print('----------------------------------------\n\n')
                        jobs.append({
                            'department': current_department,
                            'title': job_title,
                            'requirements': requirements
                        })

        # Save results to CSV
        with open('job_descriptions_with dept.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Department', 'Job Title', 'Requirements'])
            
            for job in jobs:
                writer.writerow([job['department'], job['title'], '; '.join(job['requirements'])])

    except requests.RequestException as e:
        print(f"Error fetching the main page: {e}")

if __name__ == "__main__":
    main()
