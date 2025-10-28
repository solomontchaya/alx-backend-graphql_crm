import datetime
import logging
import requests
from celery import shared_task

LOG_FILE = "/tmp/crm_report_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(message)s")

@shared_task
def generate_crm_report():
    """Fetch CRM summary from GraphQL and log the results."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = """
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json().get("data", {})
            total_customers = data.get("totalCustomers", 0)
            total_orders = data.get("totalOrders", 0)
            total_revenue = data.get("totalRevenue", 0)

            log_message = (
                f"{timestamp} - Report: {total_customers} customers, "
                f"{total_orders} orders, {total_revenue} revenue"
            )
        else:
            log_message = f"{timestamp} - Error: GraphQL returned {response.status_code}"

    except Exception as e:
        log_message = f"{timestamp} - Error generating report: {e}"

    with open(LOG_FILE, "a") as f:
        f.write(log_message + "\n")

    print(log_message)
