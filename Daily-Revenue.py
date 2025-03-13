import streamlit as st
import pandas as pd

# Function to map campid to account names
def map_accounts(data):
    """Map campid to Account Names based on specified ranges."""
    data['Account'] = pd.NA  # Initialize Account column

    # Updated Account mapping
    account_mapping = [
        (411973, 412023, 'Inuvo Fb APPD1'),
        (406651, 406669, 'Inuvo Fb APPD2 PRUDV'),
        (406556, 406570, 'Inuvo Fb APPD2 LALITH'),
        (406670, 406689, 'Inuvo Fb APPD3 CHINNU'),
        (391551, 391600, 'TRAVADO PST 10 VB'),
        (391450, 391499, 'TRAVADO PST-1'),
        (406601, 406650, 'TRAVADO PST-1'),
        (391500, 391549, 'TRAVADO PST-2 DUTT'),
        (391601, 391649, 'TRAVADO PST-2 DUTT'),
        (391801, 391850, 'TRAVADO PST-3 HZ'),
        (391851, 391900, 'TRAVADO PST-4 HZ'),
        (391650, 391699, 'TRAVADO PST 10 VB'),
        (391700, 391750, 'TRAVADO PST 6 LG'),
        (391901, 391948, 'TRAVADO PST 7 PM'),
        (391751, 391800, 'TRAVADO PST 8 HZ'),
        (406488, 406540, 'TRAVADO PST 9 LOHIT'),
        (412900, 412940, 'TRAVADO PST 9 LOHIT'),
        (406501, 406555, 'TRAVADO PST 11 PM'),
        (406571, 406600, 'TRAVADO PST 12 MB'),
        (412695, 412744, 'TRAVADO PST 13 NEW'),
        (412745, 412794, 'TRAVADO PST 14 Roy'),
        (412795, 412844, 'TRAVADO PST 15 Arn'),
        (412845, 412894, 'TRAVADO PST 16 Dnk'),
    ]

    # Apply mapping more efficiently
    for low, high, name in account_mapping:
        mask = (data['campid'] >= low) & (data['campid'] <= high)
        data.loc[mask, 'Account'] = name

    return data

# Function to process data into summaries
def process_data(raw_data):
    """Process raw data into account-wise and day-wise summaries."""
    # Ensure data types are correct
    raw_data['date'] = pd.to_datetime(raw_data['date'])

    # Map accounts
    data = map_accounts(raw_data)

    # Account-wise Summary
    account_summary = data.groupby('Account', as_index=False).agg({
        'ad_requests': 'sum',
        'matched_ad_requests': 'sum',
        'clicks': 'sum',
        'estimated_earnings': 'sum',
        'impressions': 'sum',
        'est_clicks': 'sum' if 'est_clicks' in data.columns else 'first'
    })

    # Day-wise Summary
    day_wise_summary = data.groupby(['Account', 'date'], as_index=False).agg({
        'ad_requests': 'sum',
        'matched_ad_requests': 'sum',
        'clicks': 'sum',
        'estimated_earnings': 'sum',
        'impressions': 'sum',
        'est_clicks': 'sum' if 'est_clicks' in data.columns else 'first'
    })

    return account_summary, day_wise_summary

# Streamlit App Title
st.title("FB Revenue Dashboard")

# File Uploader
uploaded_file = st.file_uploader("Upload your revenue data (CSV format)", type=["csv"])

if uploaded_file:
    try:
        # Read and validate the uploaded file
        raw_data = pd.read_csv(uploaded_file)

        # Define required and optional columns
        required_columns = {'campid', 'date', 'ad_requests', 'matched_ad_requests', 'clicks', 
                            'estimated_earnings', 'impressions'}
        optional_columns = {'est_clicks'}

        # Identify missing columns
        missing_required = required_columns - set(raw_data.columns)
        missing_optional = optional_columns - set(raw_data.columns)

        # Block processing if required columns are missing
        if raw_data.empty:
            st.error("The uploaded file is empty. Please upload a valid CSV file.")
        elif missing_required:
            st.error(f"The uploaded file is missing required columns: {', '.join(missing_required)}")
        else:
            # Warn user if optional columns are missing but allow processing
            if missing_optional:
                st.warning(f"Optional columns missing: {', '.join(missing_optional)}. The app will proceed without them.")

            # Add missing optional columns as NaN if they don’t exist
            for col in optional_columns:
                if col not in raw_data:
                    raw_data[col] = pd.NA

            # Process data
            account_summary, day_wise_summary = process_data(raw_data)

            # Sidebar for date filtering
            st.sidebar.header("Filter by Date or Time Period")
            min_date, max_date = day_wise_summary['date'].min(), day_wise_summary['date'].max()
            date_range = st.sidebar.date_input(
                "Select a Date or Date Range",
                value=(min_date, max_date) if pd.notna(min_date) and pd.notna(max_date) else None,
                key="date_range"
            )

            # Ensure filtering logic works with single date selection
            if isinstance(date_range, tuple):
                start_date, end_date = date_range
            else:
                start_date, end_date = date_range, date_range

            # Convert selected dates to Timestamp
            start_date, end_date = pd.Timestamp(start_date), pd.Timestamp(end_date)

            # Filter data
            filtered_data = day_wise_summary[
                (day_wise_summary['date'] >= start_date) &
                (day_wise_summary['date'] <= end_date)
            ]

            # Display filtered data
            st.subheader(f"Filtered Data from {start_date.date()} to {end_date.date()}")
            st.dataframe(filtered_data[['Account', 'date', 'estimated_earnings']])

            # Display Full Summaries
            st.subheader("Full Account-wise Summary")
            st.dataframe(account_summary)

            st.subheader("Day-wise Summary")
            st.dataframe(day_wise_summary)

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

else:
    st.info("Please upload a CSV file to get started.")
