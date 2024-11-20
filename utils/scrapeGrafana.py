from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


def scrapeGpuMetricsForNamespacesSelenium(namespaces, retries=2):
    base_url = "https://grafana.nrp-nautilus.io/d/dRG9q0Ymz/k8s-compute-resources-namespace-gpus?orgId=1&refresh=30s&var-namespace="
    results = {}

    chrome_options = Options()
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for namespace in namespaces:
        url = f"{base_url}{namespace}"
        print(f"Namespace: {namespace} - Attempting to scrape {url}")

        success = False
        for attempt in range(retries):
            try:
                # Load namespace page
                driver.get(url)

                # Wait dynamically for rows or specific identifiers to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "css-8fjwhi-row"))
                )

                # Parse the rendered HTML
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # Extract Pod-level GPU metrics
                gpu_data = []
                rows = soup.find_all("div", class_="css-8fjwhi-row")
                if not rows:
                    print(f"No rows found for namespace '{namespace}' on attempt {attempt + 1}")
                    continue  # Retry if no rows found

                for row in rows:
                    columns = row.find_all("div", class_=lambda value: value and "cellContainerOverflow" in value)
                    if len(columns) >= 4:
                        model = columns[0].text.strip()
                        pod_name = columns[1].text.strip()
                        gpu_requested = columns[2].text.strip()
                        gpu_utilization_percentage = columns[3].text.strip()

                        gpu_data.append({
                            "model": model,
                            "podName": pod_name,
                            "gpuRequested": gpu_requested,
                            "gpuUtilizationPercentage": gpu_utilization_percentage
                        })

                # Extract Current GPU Usage
                current_gpu_usage = None
                gpu_usage_span = soup.find("span", id="flotGaugeValue")
                if gpu_usage_span:
                    current_gpu_usage = gpu_usage_span.text.strip()

                results[namespace] = {
                    "gpuMetrics": gpu_data,
                    "currentGpuUsage": current_gpu_usage
                }
                success = True
                break  # Exit retry loop if successful

            except Exception as e:
                print(f"Error while scraping namespace '{namespace}' on attempt {attempt + 1}: {e}")
                driver.save_screenshot(f"{namespace}_error_attempt_{attempt + 1}.png")
                time.sleep(5)  # Small delay before retry

        if not success:
            results[namespace] = {"message": "Error while scraping this namespace"}

    driver.quit()
    return results


# Example Usage
if __name__ == "__main__":
    namespaces = ["gilpin-lab", "aiea-auditors", "aiea-interns"]
    gpu_metrics = scrapeGpuMetricsForNamespacesSelenium(namespaces)
    for namespace, metrics in gpu_metrics.items():
        print(f"Namespace: {namespace}")
        print(metrics)
        print()
