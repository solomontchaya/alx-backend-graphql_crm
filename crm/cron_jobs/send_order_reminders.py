#!/usr/bin/env python3
import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

def main():
    # Define date range (last 7 days)
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)

    # Configure GraphQL transport
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Define GraphQL query
    query = gql("""
        query RecentOrders($startDate: Date!, $endDate: Date!) {
            orders(orderDate_Gte: $startDate, orderDate_Lte: $endDate, status: "PENDING") {
                id
                customer {
                    email
                }
            }
        }
    """)

    # Execute query
    try:
        result = client.execute(query, variable_values={
            "startDate": str(seven_days_ago),
            "endDate": str(today)
        })

        orders = result.get("orders", [])
        if not orders:
            logging.info("No pending orders found in the last 7 days.")
        else:
            for order in orders:
                order_id = order.get("id")
                email = order.get("customer", {}).get("email")
                logging.info(f"Reminder sent for Order ID: {order_id}, Customer Email: {email}")

    except Exception as e:
        logging.error(f"Error while sending order reminders: {e}")

    print("Order reminders processed!")

if __name__ == "__main__":
    main()
