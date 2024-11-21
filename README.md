# 🌊 Nautilus Monitoring Bot 🌊

## Overview
The Nautilus Monitoring Bot is a lightweight Python-based tool designed to monitor Kubernetes namespaces on the Nautilus platform. It scrapes data for resource usage (e.g., CPU, memory, GPU) from Grafana dashboards and Kubernetes pods to detect underutilized resources and raise potential violations.

This bot is tailored for labs and research groups using Nautilus resources, enabling efficient tracking of compute resources across namespaces.

---

## 🔧 Tools and Technologies Used

- **Python**: Core programming language for scripting and automation.
- **Selenium**: Used for web scraping data from Grafana dashboards.
- **BeautifulSoup**: HTML parsing for extracting relevant metrics.
- **Kubernetes Python Client**: Fetches pod details and resource metrics directly from the Kubernetes API.
- **Grafana**: Data source for visualizing namespace GPU metrics.
- **Jenkins**: (Planned) CI/CD integration for running the bot on a schedule.
- **Docker**: (Planned) Containerization for consistent deployment.

---

## 📦 Features So Far

### ✅ Current Functionalities
1. **Namespace Resource Monitoring**:
   - Scrapes GPU metrics (utilization percentage, requested resources, pod-level details).
   - Detects and flags underutilized resources for GPUs, CPUs, and memory.
   
2. **Error Detection and Skipping**:
   - Automatically skips namespaces with "No data" or no running instances.
   - Retries scraping up to 2 times for incomplete data but handles graceful failures.

3. **Integration with Kubernetes**:
   - Fetches pod statuses directly from Kubernetes API.
   - Supports detection of "stopped" or "error" pods.

4. **Namespace-Specific Metrics**:
   - Supports multiple namespaces dynamically:
     - `gilpin-lab`
     - `aiea-auditors`
     - `aiea-interns` (empty namespaces handled automatically).

---

### 🚀 Planned Features
1. **Enhanced Logging**:
   - Centralized logs for scraping errors and warnings.
   - Clear metrics for resource violations.

2. **Periodic Reports**:
   - Daily or weekly resource utilization summaries.
   - PDF/CSV reports for lab members or administrators.

3. **Alerts and Notifications**:
   - Slack or Discord notifications for severe underutilization or resource wastage.
   - Email alerts for violations.

4. **Resource Cleanup**:
   - Automatic deletion or notification of unused pods, deployments, and resources.

---

## 🛠️ Setup and Installation

### 📂 Prerequisites
1. **Access Requirements**:
   - Nautilus admin access for all relevant namespaces.
   - A valid UCSC user email for CILogon authentication.
   - Membership in the lab with access to `kubectl` for the Kubernetes cluster.

2. **Certificates**:
   - Export and store the CILogon certificate (`cilogon.org.pem`).
   - This certificate will be used to verify HTTPS requests during bot execution.

3. **System Requirements**:
   - Python 3.9 or higher.
   - Compatible with macOS and Linux systems. (Windows support untested.)

---

### 📥 Installation Steps
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd nautilusBot
2. **Install Python Dependencies: Create and activate a virtual environment (recommended)**:
        ```bash
        python -m venv venv
        source venv/bin/activate  # For macOS/Linux
        venv\Scripts\activate  # For Windows
    -   **Install required dependencies:**
            ```bash
            pip install -r requirements.txt
3. **Download and Configure Kubernetes:**
    - Ensure `kubectl` is installed and configured for the target cluster:
        ```bash
        kubectl get namespaces
    - Verify you can access all relevant namespaces.
4. **Setup CILogon Certificate:**
    - Place the `cilogon.org.pem` certificate in the project directory.
    - Modify the code to use this certificate for HTTPS requests:
        ```bash
        requests.get(url, verify="cilogon.org.pem")
5. **Verify Selenium and ChromeDriver**:
    - Ensure Google Chrome is installed.
    - ChromeDriver is automatically downloaded via `webdriver_manager`, but you can manually install it if necessary.
6. **Run the Bot - Execute the bot script:**
    ```bash
    python main.py

---

## ⚠️ Shortfalls and Limitations

1. **Certificate Management**:
   - The `cilogon.org.pem` certificate is valid only until May 2025.
   - Future users will need to periodically export and update the certificate for HTTPS requests to remain secure.

2. **Namespace-Specific Issues**:
   - The bot currently assumes all monitored namespaces follow a similar Grafana structure. If namespaces have custom configurations, scraping may fail.

3. **Kubernetes Dependencies**:
   - The bot relies on `kubectl` being correctly configured locally. Misconfigurations or lack of access will cause errors.

4. **Error Handling**:
   - Limited retries are implemented for scraping failures.
   - Improved error messages and dynamic recovery are planned for future versions.

5. **Headless Mode**:
   - Selenium’s headless mode occasionally fails on some environments.
   - Debugging often requires turning off headless mode, which might not be ideal for automated systems.

6. **Resource Utilization**:
   - Currently, the bot only detects resource underutilization.
   - Features for identifying overutilization and optimizing resources are yet to be implemented.

---

## 🌟 Future Features

1. **📜 Detailed Logging**:
   - Implement logging mechanisms to capture detailed activity logs for all scraping and resource monitoring activities.
   - Logs will include timestamps, namespace statuses, and error traces for debugging.

2. **📊 Report Generation**:
   - Generate periodic reports summarizing resource utilization for each namespace.
   - Include graphs and tables for visual representation of data.

3. **🚨 Alerts and Notifications**:
   - Send alerts to administrators for critical violations, such as:
     - Prolonged GPU underutilization.
     - Stopped or errored pods.
     - Overprovisioned resources.
   - Integrate with Slack, email, or other communication tools for notifications.

4. **🧹 Resource Cleanup**:
   - Introduce automated cleanup processes for underutilized or idle resources to optimize cluster performance.

5. **🌐 Web Interface**:
   - Create a dashboard for live monitoring of namespaces, pods, and resource metrics.

6. **🔒 Enhanced Security**:
   - Automatically update certificates when they expire.
   - Implement OAuth2 or token-based authentication for improved security.

7. **🤖 Jenkins/Container Integration**:
   - Deploy the bot on Jenkins or Docker for seamless automation.
   - Ensure compatibility with CI/CD pipelines.

8. **📅 Scheduling**:
   - Add functionality to schedule scraping at regular intervals without manual intervention.

9. **📈 Resource Trend Analysis**:
   - Track historical resource utilization trends to identify patterns.
   - Predict resource needs using machine learning or heuristic methods.

10. **⚙️ Customizable Configurations**:
    - Allow users to configure namespaces, thresholds, and alert conditions dynamically via a configuration file.

---

## 📦 Requirements

### 🛠 Tools and Libraries
The following tools and libraries are required to run the Nautilus Bot:

| Tool/Library        | Version       | Description                                                    |
|---------------------|---------------|----------------------------------------------------------------|
| Python              | 3.10+         | Programming language used for scripting and automation.       |
| Selenium            | Latest        | For web scraping and browser automation.                     |
| BeautifulSoup       | Latest        | For parsing and extracting HTML content.                     |
| kubernetes          | Latest        | Python client for interacting with Kubernetes clusters.       |
| urllib3             | Latest        | For handling HTTP requests.                                   |
| ChromeDriverManager | Latest        | For dynamically managing ChromeDriver binaries.              |
| Google Chrome       | Latest Stable | Required for Selenium to interact with the browser.          |
| pip                 | Latest        | Python package manager to install dependencies.              |

---

### 📄 `requirements.txt`
Here’s the full list of dependencies to install using `pip`:
    beautifulsoup4==4.12.2
    kubernetes==26.1.0
    selenium==4.11.2
    webdriver-manager==3.8.6
    requests==2.31.0
    certifi==2023.7.22
    urllib3==2.0.7 


---

### 🌐 Pre-Requisites for Access
Before running the bot, ensure the following:

1. **Access to Nautilus Admin**:
   - You must have admin access to monitor all namespaces in the Nautilus cluster.

2. **UCSC Email for CILogon Authentication**:
   - A valid UCSC email is required to authenticate through CILogon for accessing cluster resources.

3. **Kubernetes Access**:
   - You must be a member of the lab with `kubectl` access configured to interact with the cluster.

---


