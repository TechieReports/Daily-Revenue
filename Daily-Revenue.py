import streamlit as st
import pandas as pd

# Function to map campid to account names
def map_accounts(data):
    """Map campid to Account Names based on specified ranges."""
    data['Account'] = pd.NA  # Initialize the Account column

    # Define ranges for accounts
    data.loc[data['campid'].between(391551, 391600), 'Account'] = 'Inuvo Fb APPD4'
    data.loc[data['campid'].between(391450, 391499), 'Account'] = 'TRAVADO PST-1'
    data.loc[data['campid'].between(406601, 406650), 'Account'] = 'TRAVADO PST-1'
    data.loc[data['campid'].between(391500, 391549), 'Account'] = 'TRAVADO PST-2'
    data.loc[data['campid'].between(391601, 391649), 'Account'] = 'TRAVADO PST-2'
    data.loc[data['campid'].between(391801, 391850), 'Account'] = 'TRAVADO PST-3'
    data.loc[data['campid'].between(391751, 391800), 'Account'] = 'TRAVADO PST-8'
    data.loc[data['campid'].between(391850, 391900), 'Account'] = 'TRAVADO PST-4'
    data.loc[data['campid'].between(391650, 391699), 'Account'] = 'TRAVADO PST-5'
    data.loc[data['campid'].between(391700, 391750), 'Account'] = 'TRAVADO PST-6'
    data.loc[data['campid'].between(391901, 391948), 'Account'] = 'TRAVADO PST-7'
    data.loc[data['campid'].between(406488, 406537), 'Account'] = 'TRAVADO PST-9'

    return data

# Function to process data into summaries
def process_data(raw_data):
    """Process raw data into account-wise and day-wise summaries."""
    # Map accounts
    data = map_accounts(raw_data)

    # Account-wise Summary
    account_summary = data.groupby('Account').agg({
        'ad_requests': 'sum',
        'matched_ad_requests': 'sum',
        'clicks': 'sum',
        'estimated_earnings': 'sum',
        'impressions': 'sum',
        'est_clicks': 'sum'
    }).reset_index()

    # Rename columns for clarity
    account_summary.rename(columns={
        'ad_requests': 'Total Ad Requests',
        'matched_ad_requests': 'Total Matched Ad Requests',
        'clicks': 'Total Clicks',
        'estimated_earnings': 'Total Estimated Earnings',
        'impressions': 'Total Impressions',
        'est_clicks': 'Total Estimated Clicks'
    }, inplace=True)

    # Day-wise Summary
    day_wise_summary = data.groupby(['Account', 'date']).agg({
        'ad_requests': 'sum',
        'matched_ad_requests': 'sum',
        'clicks': 'sum',
        'estimated_earnings': 'sum',
        'impressions': 'sum',
        'est_clicks': 'sum'
    }).reset_index()

    # Rename columns for clarity
    day_wise_summary.rename(columns={
        'date': 'Date',
        'ad_requests': 'Total Ad Requests',
        'matched_ad_requests': 'Total Matched Ad Requests',
        'clicks': 'Total Clicks',
        'estimated_earnings': 'Total Estimated Earnings',
        'impressions': 'Total Impressions',
        'est_clicks': 'Total Estimated Clicks'
    }, inplace=True)

    return account_summary, day_wise_summary

# Streamlit App Title
st.title("Daily Revenue Dashboard")

# File Uploader
uploaded_file = st.file_uploader("Upload your revenue data (CSV format)", type=["csv"])

if uploaded_file:
    # Read and process the uploaded file
    raw_data = pd.read_csv(uploaded_file)
    account_summary, day_wise_summary = process_data(raw_data)

    # Fix: Convert Date column to datetime for proper filtering
    day_wise_summary['Date'] = pd.to_datetime(day_wise_summary['Date'])
    
    # Find the latest date
    latest_date = day_wise_summary['Date'].max()
    
    # Filter data for the latest date
    latest_date_summary = day_wise_summary[day_wise_summary['Date'] == latest_date]

    # Display Latest Date Summary
    st.subheader(f"Daily Revenue for Latest Date ({latest_date.date()})")
    if not latest_date_summary.empty:
        st.dataframe(latest_date_summary[['Account', 'Total Estimated Earnings']])
    else:
        st.write("No data available for the latest date.")

    # Display Full Details Below
    st.subheader("Full Account-wise Summary")
    st.dataframe(account_summary)

    st.subheader("Day-wise Summary")
    st.dataframe(day_wise_summary)

else:
    st.info("Please upload a CSV file to get started.")
