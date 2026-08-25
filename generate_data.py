import pandas as pd
import numpy as np
import os

np.random.seed(42)

# Generate 50,000 rows of high-quality data
n_samples = 50000

# Annual Income (log-normal, bounded)
annual_income = np.random.lognormal(mean=11.15, sigma=0.6, size=n_samples)
annual_income = np.clip(annual_income, 10000, 1000000).round()

# Loan Amount (proportional to income with some randomness, capped)
loan_amount = annual_income * np.random.uniform(0.05, 0.4, size=n_samples)
loan_amount = np.clip(loan_amount, 500, 500000).round()

# Credit Score (skewed towards higher scores, bounded 300-850)
credit_score = np.random.normal(loc=710, scale=80, size=n_samples)
credit_score = np.clip(credit_score, 300, 850).round().astype(int)

# Debt to Income Ratio (normal, bounded 0-1)
dti = np.random.normal(loc=0.25, scale=0.15, size=n_samples)
dti = np.clip(dti, 0.0, 1.0).round(4)

# Years Employed (exponential, bounded 0-50)
years_employed = np.random.exponential(scale=7.0, size=n_samples)
years_employed = np.clip(years_employed, 0.0, 50.0).round(1)

# Delinquencies (poisson, usually 0)
delinquencies = np.random.poisson(lam=0.3, size=n_samples)
delinquencies = np.clip(delinquencies, 0, 30).astype(int)

df = pd.DataFrame({
    'annual_income': annual_income,
    'loan_amount': loan_amount,
    'credit_score': credit_score,
    'debt_to_income_ratio': dti,
    'years_employed': years_employed,
    'delinquencies_last_2yrs': delinquencies
})

# Add a few intentional bad rows to test the error logging feature of the site
df.loc[15, 'credit_score'] = 950 # Invalid credit score
df.loc[150, 'annual_income'] = -5000 # Invalid income
df.loc[4500, 'debt_to_income_ratio'] = 1.5 # Invalid DTI

output_path = r'C:\Users\eyar1\ECOM\antigravity works\Project_Loan\Kaggle_Equivalent_Loan_Data_50k.csv'
df.to_csv(output_path, index=False)

print(f"Generated large dataset at {output_path} with {len(df)} rows.")
