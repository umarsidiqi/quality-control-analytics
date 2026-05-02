# =============================================================================
# Manufacturing Quality Control Analytics
# Author: Muhammad Umar Siddiqui
# Description: End-to-end quality data analysis to identify defect patterns,
#              failure trends, and quality KPIs across production lines.
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# --- Style -------------------------------------------------------------------
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150
})
BLUE   = '#1A5691'
ORANGE = '#E07B39'
GREEN  = '#3A8C5C'
RED    = '#C0392B'
GRAY   = '#7F8C8D'
PALETTE = [BLUE, ORANGE, GREEN, RED, GRAY]

# =============================================================================
# 1. LOAD & VALIDATE DATA
# =============================================================================
df = pd.read_csv('data/manufacturing_quality_data.csv', parse_dates=['Date'])

print("=" * 60)
print("DATASET OVERVIEW")
print("=" * 60)
print(f"Total Records      : {len(df):,}")
print(f"Date Range         : {df['Date'].min().date()} to {df['Date'].max().date()}")
print(f"Product Lines      : {df['Product_Line'].nunique()}")
print(f"Defect Categories  : {df['Defect_Type'].nunique() - 1}")
print(f"Missing Values     : {df.isnull().sum().sum()}")
print()

# =============================================================================
# 2. FEATURE ENGINEERING
# =============================================================================
df['Month']        = df['Date'].dt.to_period('M')
df['Month_Label']  = df['Date'].dt.strftime('%b %Y')
df['Quarter']      = df['Date'].dt.to_period('Q').astype(str)
df['Is_Defective'] = (df['Defect_Type'] != 'No Defect').astype(int)

# =============================================================================
# 3. KEY QUALITY KPIs
# =============================================================================
total_units     = df['Units_Inspected'].sum()
total_defects   = df['Defects_Found'].sum()
overall_defect_rate = (total_defects / total_units * 100)
pass_rate       = df['Pass'].mean() * 100
fail_rate       = 100 - pass_rate
top_defect      = df[df['Defect_Type'] != 'No Defect']['Defect_Type'].value_counts().idxmax()
worst_line      = df.groupby('Product_Line')['Defect_Rate_%'].mean().idxmax()

print("=" * 60)
print("KEY QUALITY KPIs")
print("=" * 60)
print(f"Total Units Inspected  : {total_units:,}")
print(f"Total Defects Found    : {total_defects:,}")
print(f"Overall Defect Rate    : {overall_defect_rate:.2f}%")
print(f"Pass Rate              : {pass_rate:.1f}%")
print(f"Fail Rate              : {fail_rate:.1f}%")
print(f"Most Common Defect     : {top_defect}")
print(f"Highest Defect Line    : {worst_line}")
print()

# =============================================================================
# 4. VISUALIZATIONS
# =============================================================================

# --- 4.1 Monthly Defect Rate Trend -------------------------------------------
monthly = df.groupby('Month').agg(
    Units=('Units_Inspected', 'sum'),
    Defects=('Defects_Found', 'sum')
).reset_index()
monthly['Defect_Rate'] = (monthly['Defects'] / monthly['Units'] * 100).round(2)
monthly['Month_dt'] = monthly['Month'].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(12, 4.5))
ax.plot(monthly['Month_dt'], monthly['Defect_Rate'], color=BLUE, linewidth=2.2, marker='o', markersize=5)
ax.fill_between(monthly['Month_dt'], monthly['Defect_Rate'], alpha=0.12, color=BLUE)
ax.axhline(monthly['Defect_Rate'].mean(), color=RED, linestyle='--', linewidth=1.4, label=f"Average: {monthly['Defect_Rate'].mean():.2f}%")
ax.set_title('Monthly Defect Rate Trend (Jan 2023 – Dec 2024)')
ax.set_xlabel('Month')
ax.set_ylabel('Defect Rate (%)')
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
ax.legend()
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('outputs/01_monthly_defect_trend.png', bbox_inches='tight')
plt.close()
print("Chart saved: 01_monthly_defect_trend.png")

# --- 4.2 Defect Rate by Product Line -----------------------------------------
line_stats = df.groupby('Product_Line').agg(
    Units=('Units_Inspected', 'sum'),
    Defects=('Defects_Found', 'sum')
).reset_index()
line_stats['Defect_Rate'] = (line_stats['Defects'] / line_stats['Units'] * 100).round(2)
line_stats = line_stats.sort_values('Defect_Rate', ascending=True)

fig, ax = plt.subplots(figsize=(9, 4.5))
bars = ax.barh(line_stats['Product_Line'], line_stats['Defect_Rate'],
               color=[RED if x == line_stats['Defect_Rate'].max() else BLUE for x in line_stats['Defect_Rate']],
               edgecolor='white', height=0.55)
for bar, val in zip(bars, line_stats['Defect_Rate']):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
            f'{val:.2f}%', va='center', fontsize=10)
ax.set_title('Defect Rate by Product Line')
ax.set_xlabel('Defect Rate (%)')
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
plt.tight_layout()
plt.savefig('outputs/02_defect_rate_by_product_line.png', bbox_inches='tight')
plt.close()
print("Chart saved: 02_defect_rate_by_product_line.png")

# --- 4.3 Defect Type Breakdown (excluding No Defect) -------------------------
defect_counts = df[df['Defect_Type'] != 'No Defect']['Defect_Type'].value_counts()

fig, ax = plt.subplots(figsize=(8, 5))
wedges, texts, autotexts = ax.pie(
    defect_counts.values,
    labels=defect_counts.index,
    autopct='%1.1f%%',
    colors=PALETTE,
    startangle=140,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
)
for at in autotexts:
    at.set_fontsize(10)
ax.set_title('Defect Type Distribution')
plt.tight_layout()
plt.savefig('outputs/03_defect_type_breakdown.png', bbox_inches='tight')
plt.close()
print("Chart saved: 03_defect_type_breakdown.png")

# --- 4.4 Pass/Fail Rate by Shift ---------------------------------------------
shift_stats = df.groupby('Shift').agg(
    Pass=('Pass', 'sum'),
    Total=('Pass', 'count')
).reset_index()
shift_stats['Pass_Rate'] = (shift_stats['Pass'] / shift_stats['Total'] * 100).round(1)
shift_stats['Fail_Rate'] = 100 - shift_stats['Pass_Rate']

x = np.arange(len(shift_stats))
width = 0.38
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(x - width/2, shift_stats['Pass_Rate'], width, label='Pass Rate', color=GREEN, edgecolor='white')
ax.bar(x + width/2, shift_stats['Fail_Rate'], width, label='Fail Rate', color=RED, edgecolor='white')
ax.set_xticks(x)
ax.set_xticklabels(shift_stats['Shift'])
ax.set_ylabel('Rate (%)')
ax.set_title('Pass vs Fail Rate by Shift')
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
ax.legend()
for i, row in shift_stats.iterrows():
    ax.text(i - width/2, row['Pass_Rate'] + 0.5, f"{row['Pass_Rate']}%", ha='center', fontsize=9)
    ax.text(i + width/2, row['Fail_Rate'] + 0.5, f"{row['Fail_Rate']}%", ha='center', fontsize=9)
plt.tight_layout()
plt.savefig('outputs/04_pass_fail_by_shift.png', bbox_inches='tight')
plt.close()
print("Chart saved: 04_pass_fail_by_shift.png")

# --- 4.5 Quarterly Defect Trend Heatmap --------------------------------------
heatmap_data = df.groupby(['Quarter', 'Product_Line'])['Defect_Rate_%'].mean().unstack()

fig, ax = plt.subplots(figsize=(11, 4))
sns.heatmap(heatmap_data.T, annot=True, fmt='.1f', cmap='YlOrRd',
            linewidths=0.5, ax=ax, cbar_kws={'label': 'Avg Defect Rate (%)'})
ax.set_title('Quarterly Defect Rate Heatmap by Product Line')
ax.set_xlabel('Quarter')
ax.set_ylabel('')
plt.tight_layout()
plt.savefig('outputs/05_quarterly_heatmap.png', bbox_inches='tight')
plt.close()
print("Chart saved: 05_quarterly_heatmap.png")

# =============================================================================
# 5. SUMMARY TABLE FOR POWER BI EXPORT
# =============================================================================
summary = df.groupby(['Month_Label', 'Product_Line', 'Defect_Type', 'Shift']).agg(
    Units_Inspected=('Units_Inspected', 'sum'),
    Defects_Found=('Defects_Found', 'sum'),
    Total_Inspections=('Pass', 'count'),
    Pass_Count=('Pass', 'sum')
).reset_index()
summary['Defect_Rate_%'] = (summary['Defects_Found'] / summary['Units_Inspected'] * 100).round(2)
summary['Pass_Rate_%']   = (summary['Pass_Count'] / summary['Total_Inspections'] * 100).round(1)
summary.to_csv('outputs/quality_summary_for_powerbi.csv', index=False)
print("Power BI export saved: quality_summary_for_powerbi.csv")

print()
print("=" * 60)
print("ANALYSIS COMPLETE — all outputs saved to /outputs folder")
print("=" * 60)
