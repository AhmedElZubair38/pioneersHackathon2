# TransferTimeMatrix class represents the transfer times between different locations.
import pandas as pd

class TransferTimeMatrix:

    def __init__(self, transfer_data):
        self.transfer_data = transfer_data  # A DataFrame with transfer times

    def get_transfer_time(self, origin, destination):
        if pd.isna(self.transfer_data.at[origin, destination]):
            return float('inf')  # No link between origin and destination
        else:
            return int(self.transfer_data.at[origin, destination].replace(',', ''))  # Remove commas and convert to integer