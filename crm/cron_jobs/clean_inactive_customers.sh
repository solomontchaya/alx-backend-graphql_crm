#!/bin/bash

# Navigate to the Django project directory (update path if necessary)
cd "$(dirname "$0")/../.." || exit

# Activate virtual environment if needed
# source venv/bin/activate

# Define log file
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Run Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from datetime import timedelta, date
from crm.models import Customer
from django.utils import timezone

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(orders__isnull=True, created_at__lt=one_year_ago)
deleted_count, _ = inactive_customers.delete()
print(deleted_count)
")

# Log timestamp and deleted count
echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$DELETED_COUNT inactive customers\" >> \"$LOG_FILE\"
