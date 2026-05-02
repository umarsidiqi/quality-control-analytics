import pandas as pd
import numpy as np

np.random.seed(42)

n = 2000
months = pd.date_range(start='2023-01-01', end='2024-12-31', freq='ME')

product_lines = ['Assembly A', 'Assembly B', 'Component X', 'Component Y', 'Sub-System Z']
defect_types = ['Surface Defect', 'Dimensional Error', 'Material Flaw', 'Assembly Fault', 'No Defect']
shifts = ['Morning', 'Afternoon', 'Night']
inspectors = ['Inspector 1', 'Inspector 2', 'Inspector 3', 'Inspector 4']

defect_weights = {
    'Assembly A':    [0.10, 0.08, 0.05, 0.12, 0.65],
    'Assembly B':    [0.08, 0.06, 0.07, 0.09, 0.70],
    'Component X':   [0.15, 0.10, 0.08, 0.06, 0.61],
    'Component Y':   [0.07, 0.12, 0.09, 0.05, 0.67],
    'Sub-System Z':  [0.12, 0.09, 0.11, 0.08, 0.60],
}

records = []
for i in range(n):
    date = np.random.choice(pd.date_range('2023-01-01', '2024-12-31', freq='D'))
    product = np.random.choice(product_lines)
    weights = defect_weights[product]
    defect = np.random.choice(defect_types, p=weights)
    shift = np.random.choice(shifts)
    inspector = np.random.choice(inspectors)
    units_inspected = np.random.randint(50, 300)
    defects_found = 0 if defect == 'No Defect' else np.random.randint(1, 15)

    records.append({
        'Date': date,
        'Product_Line': product,
        'Defect_Type': defect,
        'Shift': shift,
        'Inspector': inspector,
        'Units_Inspected': units_inspected,
        'Defects_Found': defects_found,
        'Pass': 1 if defect == 'No Defect' else 0
    })

df = pd.DataFrame(records)
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date').reset_index(drop=True)
df['Defect_Rate_%'] = (df['Defects_Found'] / df['Units_Inspected'] * 100).round(2)
df.to_csv('/home/claude/quality_project/data/manufacturing_quality_data.csv', index=False)
print(f"Dataset generated: {len(df)} records")
print(df.head())
