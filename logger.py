import json
import datetime
import random
import os

class LocalJsonLogger:
    def __init__(self, log_file_name):
        self.log_file_name = log_file_name
        self.log_data = []

        # Create a new log file locally
        self.create_new_log_file()

    def create_new_log_file(self):
        """Create an empty JSON log file locally."""
        # Check if the log file already exists, and if not, create it
        if not os.path.exists(self.log_file_name):
            with open(self.log_file_name, 'w') as file:
                json.dump([], file, indent=4)
            print(f"New log file '{self.log_file_name}' created.")
        else:
            print(f"Log file '{self.log_file_name}' already exists. Appending to it.")

    def append_log(self, new_entry):
        """Append new log entry and update the file locally."""
        # Add new entry to local log data
        self.log_data.append(new_entry)
        
        # Update the log file locally
        with open(self.log_file_name, 'w') as file:
            json.dump(self.log_data, file, indent=4)
        print(f"Appended new entry to '{self.log_file_name}'.")

    def generate_log_entry(self):
        """Generate a new log entry with random data (simulating a trading strategy)."""
        return {
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tsymbol": f"BANKNIFTY23OCT24C{random.randint(50000, 60000)}",
            "orderno": f"{random.randint(10000000000000, 99999999999999)}",
            "type": random.choice(["B", "S"]),
            "quantity": str(random.randint(10, 100)),
            "ordered_price": round(random.uniform(100.0, 300.0), 2),
            "executed_price": round(random.uniform(100.0, 300.0), 2),
            "executed_quantity": str(random.randint(10, 100)),
            "order_type": random.choice(["MKT", "LMT", "update"]),
            "status": random.choice(["placed", "open", "pending", "completed"])
        }

# if __name__ == "__main__":
#     # Configuration
#     log_file_name = f"trading_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{random.randint(100, 999)}.json"

#     # Initialize the local JSON logger
#     logger = LocalJsonLogger(log_file_name)

#     # Simulate logging dynamic data during strategy execution
#     for _ in range(10):  # Simulate 10 log entries
#         new_entry = logger.generate_log_entry()
#         logger.append_log(new_entry)
