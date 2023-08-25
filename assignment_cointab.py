# -*- coding: utf-8 -*-
"""Assignment_cointab.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ibfPhgDxuqry5W7eYZWJMdiDZQND2HeP
"""

# Import necessary libraries

import pandas as pd
import numpy as np

# Load data from Excel files
Orders = pd.read_excel("/content/Company X - Order Report.xlsx")
Pincode_Zone = pd.read_excel("/content/Company X - Pincode Zones.xlsx")
SKU_Master = pd.read_excel("/content/Company X - SKU Master.xlsx")
Courier_invoice = pd.read_excel("/content/Courier Company - Invoice.xlsx")
Courier_Rates = pd.read_excel("/content/Courier Company - Rates.xlsx")

# Rename a column in 'Orders' DataFrame
Orders.rename(columns={'ExternOrderNo':'Order ID'}, inplace = True)

# Merge 'Orders' and 'SKU_Master' DataFrames
merged_data = Orders.merge(SKU_Master, on='SKU')
merged_data.head()

# Calculate 'Total Weight' and 'Total_price' columns
merged_data['Total Weight'] = merged_data['Order Qty'] * merged_data['Weight (g)']
merged_data['Total_price'] = merged_data['Order Qty'] * merged_data['Item Price(Per Qty.)']

merged_data.head()

# Drop unnecessary columns
columns_to_drop = ['Order Qty', 'Item Price(Per Qty.)', 'Weight (g)']
merged_data.drop(columns=columns_to_drop, inplace=True)

# Group data by 'Order ID' and perform aggregation
grouped = merged_data.groupby('Order ID').agg({'Total Weight': 'sum', 'Total_price': 'sum', 'Payment Mode': 'first'})
grouped.reset_index(inplace=True)

grouped['Total Weight'] = (grouped['Total Weight'] / 1000).round(2)
grouped.head()

merged_data = grouped.merge(Courier_invoice, on='Order ID')

aplicable_weight = pd.DataFrame(merged_data[['Order ID','Total Weight', 'Customer Pincode']])

# Merge 'aplicable_weight' with 'Pincode_Zone'
aplicable_weight.drop_duplicates(subset='Customer Pincode', inplace=True)
aplicable_weight_merged = aplicable_weight.merge(Pincode_Zone, on='Customer Pincode', how='inner')

# Create a DataFrame 'aplicable_weight' with selected columns
Courier_Rates['Zone'] = Courier_Rates['Zone'].str.lower()
aplicable_weight_merged = aplicable_weight_merged.merge(Courier_Rates, on='Zone')

aplicable_weight_merged.head()

aplicable_weight = aplicable_weight_merged[['Order ID', 'Total Weight', 'Zone', 'Weight Slabs']]

aplicable_weight.count()

# Loop through 'aplicable_weight' DataFrame to calculate 'Aplicable weight'
for i in range(len(aplicable_weight)):
    if aplicable_weight['Total Weight'][i] <= aplicable_weight['Weight Slabs'][i]:
        aplicable_weight.at[i, 'Aplicable weight'] = aplicable_weight['Total Weight'][i]
    else:
        additional_slab = (aplicable_weight['Total Weight'][i] // aplicable_weight['Weight Slabs'][i]) + 1
        aplicable_weight.at[i, 'Aplicable weight'] = aplicable_weight['Weight Slabs'][i] * additional_slab

# Drop the duplicate column
#aplicable_weight.drop(columns=['Aplicable weight'], inplace=True)

Order_data = aplicable_weight.merge(Courier_invoice, on='Order ID')
Order_data.head()

Order_data.drop(columns=['Warehouse Pincode'], inplace=True)
Order_data = Order_data.rename(columns={'Zone_x':'Zone'})

Order_data.head()

Order_data = Order_data.merge(Courier_Rates, on='Zone')

Order_data.head()

Total_charges = Order_data.drop(columns=['Total Weight'])
Total_charges.head()

# Loop through 'Total_charges' to calculate charges based on conditions
for i in range(len(Total_charges)):
  if Total_charges['Type of Shipment'][i] == 'Forward charges':

    if Total_charges['Aplicable weight'][i] <= Total_charges['Weight Slabs_x'][i]:
       Total_charges.at[i, 'Total_charges'] = Total_charges['Forward Fixed Charge'][i]
    else:
        additional_slab = Total_charges['Aplicable weight'][i] // Total_charges['Weight Slabs_x'][i]
        Total_charges.at[i, 'Total_charges'] = (Total_charges['Forward Fixed Charge'][i] +
                                                Total_charges['Forward Additional Weight Slab Charge'][i]*  additional_slab)

  else:

    if Total_charges['Aplicable weight'][i] <= Total_charges['Weight Slabs_x'][i]:
       Total_charges.at[i, 'Total_charges'] = Total_charges['Forward Fixed Charge'][i] + Total_charges['RTO Fixed Charge'][i]

    else:
      additional_slab = Total_charges['Aplicable weight'][i] // Total_charges['Weight Slabs_x'][i]
      Total_charges.at[i, 'Total_charges'] = (Total_charges['Forward Fixed Charge'][i] +
                                                Total_charges['Forward Additional Weight Slab Charge'][i]*  additional_slab) + (
                                                Total_charges['RTO Fixed Charge'][i] + Total_charges['RTO Additional Weight Slab Charge'][i] *
                                                additional_slab )

Total_charges.head()

Total_charges = Total_charges.merge(grouped, on='Order ID')

# Loop through 'Total_charges' to calculate 'COD_Charge' and 'Total_charge'
for i in range(len(Total_charges)):
for i in range(len(Total_charges)):
  if Total_charges['Payment Mode'][i] == 'COD':
    if Total_charges['Total_price'][i] <= 300:
      Total_charges.at[i, 'COD_Charge'] = 15
    else:
       Total_charges.at[i, 'COD_Charge'] = Total_charges['Total_price'][i] * 0.05

  else:
     Total_charges.at[i, 'COD_Charge'] = 0
  Total_charges['Total_charge'] = Total_charges['Total_charges'] + Total_charges['COD_Charge']

Total_charges.tail()

Courier_Rates = Courier_Rates.rename(columns={'Zone':'Zone_y'})
Courier_Rates = Courier_Rates[['Zone_y', 'Weight Slabs']]
Total_charges = Total_charges.merge(Courier_Rates, on='Zone_y')

Total_charges.head()

Total_charges['Difference'] = (Total_charges['Total_charge'] - Total_charges['Billing Amount (Rs.)']).round(2)
Total_charges.head()

# Create 'Order_level_output' DataFrame with selected columns
Order_level_output = Total_charges[['Order ID', 'AWB Code', 'Total Weight', 'Weight Slabs_x', 'Charged Weight','Weight Slabs', 'Zone',
                                    'Zone_y', 'Total_charge', 'Billing Amount (Rs.)', 'Difference']]

# Rename columns for clarity
Order_level_output= Order_level_output.rename(columns={'Total Weight':'Total weight as per X (KG)',
                                                      'Charged Weight': 'Total weight as per Courier Company (KG)',
                                                      'Zone':'Delivery Zone as per X', 'Zone_y':'Delivery Zone charged by Courier Company',
                                                      'Total_charge':'Expected Charge as per X (Rs.)',
                                                      'Billing Amount (Rs.)':'Charges Billed by Courier Company (Rs.)'})

Order_level_output

# Calculate matches and mismatches for 'Delivery Zone
match = 0
mis_match = 0

for i in range(len(Order_level_output)):
  if Order_level_output['Delivery Zone as per X'][i] == Order_level_output[' Total weight as per Courier Company (KG)'][i]:
    match += 1

  else:
    mis_match += 1

print("Zone_matched: ", match)
print("Zone_mis_matched: ", mis_match)

"""
After analyzing the data, the following results were obtained:

- **Total Orders Analyzed:** 124
- **Orders with Zone Match:** 59
- **Orders with Zone Mismatch:** 65

## Understanding the Zone Mismatch

The "Zone Mismatch" occurs when the delivery zones assigned by the e-commerce company do not match the delivery zones charged by the courier company. This mismatch can lead to discrepancies in the calculation of courier charges and, subsequently, in the billed amounts.
"""

# Calculate counts and sums for different order statuses
currectly_charged =  over_charged = under_charged = 0
sum1 = sum2 = sum3 = 0
for i in range(len(Order_level_output)):
  if Order_level_output['Difference'][i] == 0:
    currectly_charged += 1
    sum1 += Order_level_output['Charges Billed by Courier Company (Rs.)'][i]
  elif Order_level_output['Difference'][i] < 0:
    over_charged += 1
    sum2 += abs(Order_level_output['Difference'][i])
  else:
    under_charged += 1
    sum3 += Order_level_output['Difference'][i]

# Create 'Summary_Table' DataFrame
Summary_Table = pd.DataFrame({'Order_Status':['Total orders where X has been correctly charged', 'Total Orders where X has been overcharged',
                                              'Total Orders where X has been undercharged'], 'Count': [currectly_charged, over_charged, under_charged],
                                              'Amount (Rs.)':[sum1, sum2, sum3]})

Summary_Table

"""The analysis was conducted on a subset of orders, resulting in the following findings:

| Order Status                                  | Count | Amount (Rs.) |
|-----------------------------------------------|-------|--------------|
| Total orders where X has been correctly charged | 5     | 316.60       |
| Total Orders where X has been overcharged      | 59    | 2615.55      |
| Total Orders where X has been undercharged     | 60    | 12115.00     |
## Explanation

1. **Correctly Charged Orders:** There are 5 orders where the e-commerce company's calculated charges match the billed amounts from the courier company. This indicates accurate billing for these orders.

2. **Overcharged Orders:** A total of 59 orders have been overcharged, resulting in a cumulative overcharge amount of Rs. 2615.55. Overcharging occurs when the billed amounts from the courier company exceed the calculated charges by the e-commerce company.

3. **Undercharged Orders:** The analysis identified 60 orders that were undercharged, leading to a total undercharge amount of Rs. 12115.00. Undercharging happens when the calculated charges by the e-commerce company are higher than the billed amounts from the courier company.

## Impact and Implications

The observed discrepancies in courier charges have several implications:

- **Billing Accuracy:** Overcharged orders raise concerns about the accuracy of billing by the courier company, potentially affecting the e-commerce company's trust in the billing process.

- **Financial Impact:** Overcharged amounts contribute to additional costs for the e-commerce company, affecting financial planning and profitability.

- **Operational Efficiency:** Addressing undercharged orders ensures that the courier company receives appropriate compensation for its services, maintaining a balanced partnership.

## Recommendations

To address the discrepancies in courier charges and ensure accurate billing, consider the following actions:

1. **Verification and Reconciliation:** Regularly verify and reconcile the calculated charges by the e-commerce company with the billed amounts from the courier company.

2. **Billing Transparency:** Communicate openly with the courier company about discrepancies, seek clarification, and request detailed billing information.

3. **Review Agreement:** Review the terms and conditions of the agreement between the e-commerce company and the courier company to ensure alignment in billing practices.

4. **Data Quality:** Maintain accurate and up-to-date order and charge data to facilitate accurate billing calculations.


"""

# Set up directory and file names for saving
import os

directory_path = 'C:/Users/ELCOT/Desktop/Assignment_Result'
file_name = 'Summary_table.xlsx'

# Create directory if it doesn't exist
if not os.path.exists(directory_path):
    os.makedirs(directory_path)
# Create full file path

file_path = os.path.join(directory_path, file_name)

try:
   # Save 'Summary_Table' DataFrame to Excel file
    Summary_Table.to_excel(file_path, index=False, engine='xlsxwriter')
    print("Excel file saved successfully.")
except Exception as e:
    print("An error occurred:", e)

# Set up directory and file names for saving 'Order_level_output'
directory_path = 'C:/Users/ELCOT/Desktop/Assignment_Result'
file_name = 'Order_level_Output.xlsx'

if not os.path.exists(directory_path):
    os.makedirs(directory_path)
# Create full file path
file_path = os.path.join(directory_path, file_name)

Order_level_output.to_excel(file_path, index=False, engine='xlsxwriter')
