import streamlit as st
import pandas as pd

# Function to map campid to account names
def map_accounts(data):
    """Map campid to Account Names based on specified ranges."""
    data['Account'] = pd.NA  # Initialize the Account column

    # Updated Account mapping
    account_mapping = {
        (411973, 412023): 'Inuvo Fb APPD1',
        (406651, 406669): 'Inuvo Fb APPD2 PRUDV',
        (406556, 406570): 'Inuvo Fb APPD2 LALITH',
        (406670, 406689): 'Inuvo Fb APPD3 CHINNU',
        (391551, 391600): 'TRAVADO PST 10 VB',
        (391450, 391499): 'TRAVADO PST-1',
        (406601, 406650): 'TRAVADO PST-1',
        (391500, 391549): 'TRAVADO PST-2 DUTT',
        (391601, 391649): 'TRAVADO PST-2 DUTT',
        (391801, 391850): 'TRAVADO PST-3 HZ',
        (391851, 391900): 'TRAVADO PST-4 HZ',
        (391650, 391699): 'TRAVADO PST 10 VB',
        (391700, 391750): 'TRAVADO PST 6 LG',
        (391901, 391948): 'TRAVADO PST 7 PM',
        (391751, 391800): 'TRAVADO PST 8 HZ',
        (406488, 406500): 'TRAVADO PST 9 FRED',
        (406501, 406555): 'TRAVADO PST 11 PM',
        (406571, 406600): 'TRAVADO PST 12 MB',
        (412695, 412744): 'TRAVADO PST 13 NEW',
        (412745, 412794): 'TRAVADO PST 14 Roy',
        (412795, 412844): 'TRAVADO PST 15 Arn',
        (412845, 412894): 'TRAVADO PST 16 Dnk',
    }

    for (low, high), name in account_mapping.items():
        data.loc[data['campid'].between(low, high), 'Account'] = name
    
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
st.title("FB Revenue Dashboard")

# File Uploader
uploaded_file = st.file_uploader("Upload your revenue data (CSV format)", type=["csv"])

if uploaded_file:
    try:
        # Read and validate the uploaded file
        raw_data = pd.read_csv(uploaded_file)
        if raw_data.empty:
            st.error("The uploaded file is empty. Please upload a valid CSV file.")
        elif not {'campid', 'date', 'ad_requests', 'matched_ad_requests', 'clicks', 
                  'estimated_earnings', 'impressions', 'est_clicks'}.issubset(raw_data.columns):
            st.error("The uploaded file does not contain all the required columns. Please check your data.")
        else:
            # Process data if valid
            account_summary, day_wise_summary = process_data(raw_data)

            # Convert Date column to datetime
            day_wise_summary['Date'] = pd.to_datetime(day_wise_summary['Date'])
            
            # Add a dynamic date filter
            st.sidebar.header("Filter by Date or Time Period")
            date_range = st.sidebar.date_input(
                "Select a Date or Date Range",
                value=(day_wise_summary['Date'].min(), day_wise_summary['Date'].max()),
                key="date_range"
            )

            # Handle single date or date range
            if isinstance(date_range, tuple):
                start_date, end_date = date_range
            else:
                start_date, end_date = date_range, date_range

            # Filter data based on the selected date range
            filtered_data = day_wise_summary[
                (day_wise_summary['Date'] >= pd.Timestamp(start_date)) &
                (day_wise_summary['Date'] <= pd.Timestamp(end_date))
            ]

            # Display filtered data
            st.subheader(f"Filtered Data from {start_date} to {end_date}")
            st.dataframe(filtered_data[['Account', 'Date', 'Total Estimated Earnings']])

            # Display Full Details Below
            st.subheader("Full Account-wise Summary")
            st.dataframe(account_summary)

            st.subheader("Day-wise Summary")
            st.dataframe(day_wise_summary)

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

else:
    st.info("Please upload a CSV file to get started.")
