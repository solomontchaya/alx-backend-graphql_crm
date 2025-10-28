import datetime
import requests
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

def update_low_stock():
    """Triggers the GraphQL mutation to restock low-stock products."""
    log_file = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    query = """
    mutation {
        updateLowStockProducts {
            success
            updatedProducts {
                id
                name
                stock
            }
        }
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json().get("data", {}).get("updateLowStockProducts", {})
            success_msg = data.get("success", "No success message.")
            updated_products = data.get("updatedProducts", [])

            with open(log_file, "a") as f:
                f.write(f"{timestamp} - {success_msg}\n")
                for p in updated_products:
                    f.write(f"  → {p['name']} (Stock: {p['stock']})\n")
        else:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} - Failed with status {response.status_code}\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Error: {e}\n")

def log_crm_heartbeat():
    """Logs a timestamped heartbeat message and optionally checks GraphQL endpoint."""
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Optional: verify GraphQL endpoint responsiveness
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200 and "data" in response.json():
            message += " (GraphQL OK)"
        else:
            message += " (GraphQL check failed)"
    except Exception:
        message += " (GraphQL unreachable)"

    # Append log message
    with open(log_file, "a") as f:
        f.write(message + "\n")
