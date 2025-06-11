import streamlit as st

# ✅ This MUST be the first Streamlit command
st.set_page_config(page_title="Zoom Info Company Details Extractor", layout="centered")

import pandas as pd
import re
from auth import check_login

# ✅ Login check (after set_page_config)
if not check_login():
    st.stop()

st.title("📄 ZICD Extractor")

# State abbreviation map
state_abbr = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
    'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
    'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
    'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
    'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
    'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
    'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
    'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
    'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
    'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
    'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
    'wisconsin': 'WI', 'wyoming': 'WY'
}

# Address parsing helper
def parse_address(address):
    address = address.replace("United States", "").strip().rstrip(",")
    match = re.match(r"(.+?),\s*([^,]+),\s*([A-Za-z ]+)[,\s]*(\d{0,5})?", address)
    if match:
        street, city, state, zipcode = match.groups()
        state_cleaned = state.strip().lower()
        state_abbreviated = state_abbr.get(state_cleaned, state.strip().upper())
        return (
            street.strip() if street else "Not Available",
            city.strip() if city else "Not Available",
            state_abbreviated if state else "Not Available",
            zipcode.strip() if zipcode else "Not Available"
        )
    else:
        return "Not Available", "Not Available", "Not Available", "Not Available"

if 'input_text' not in st.session_state:
    st.session_state.input_text = ""

def clear_input():
    st.session_state.input_text = ""

# Placeholder
placeholder_text = """MEB Management Services
Likely to Engage tag.
Highly Engaged Employees
Real Estate · Arizona, United States · 600 Employees

View Company Info for Free

Overview
Headquarters
11201 N Tatum Blvd Ste 260, Phoenix, Arizona, 8...
Phone Number
(602) 279-5515
Website
www.mebapts.com
Revenue
$614.8 Million
Industry
Real Estate"""

st.text_area("Copy and Paste the data from this link https://www.ZICD.com/c/sequoia-equities-inc/107545593", height=300, key='input_text', placeholder=placeholder_text)

col1, col2 = st.columns([1, 1])
with col1:
    extract_clicked = st.button("Extract Company Details")
with col2:
    st.button("Clear", on_click=clear_input)

if extract_clicked:
    input_data = st.session_state.input_text
    if input_data:
        lines = input_data.splitlines()
        lines = [line.strip() for line in lines if line.strip()]

        data_dict = {}
        company_name = lines[0].strip()
        data_dict['Office Name'] = company_name

        num_employees = "Not Available"
        for i in range(1, min(6, len(lines))):
            match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*Employees', lines[i])
            if match:
                num_employees = match.group(1).replace(",", "")
                break

        for i in range(len(lines)):
            line = lines[i].strip()
            if line in ["About", "View Company Info for Free"]:
                continue
            if i % 2 == 0:
                key = line.rstrip(':')
            else:
                value = line if line else "Not Available"
                data_dict[key] = value

        data_dict['Staff Count'] = num_employees
        street, city, state, zipcode = parse_address(data_dict.get('Headquarters', ''))
        data_dict['Office Address'] = street
        data_dict['Office City'] = city
        data_dict['Office State'] = state
        data_dict['Office Zip'] = zipcode

        required_columns = [
            'Office Name', 'Office Address', 'Office City', 'Office State',
            'Office Zip', 'Phone Number', 'Staff Count', 'Website', 'Revenue',
            'Industry', 'Stock Symbol'
        ]

        for col in required_columns:
            if col not in data_dict:
                data_dict[col] = "Not Available"

        df = pd.DataFrame([data_dict])
        df = df[required_columns]

        formatted_data = "\n".join(df.apply(lambda row: "\t".join(row.astype(str)), axis=1))

        st.subheader("📋 Copy Extracted Data")
        st.code(formatted_data, language="text")

        csv_str = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_str.encode('utf-8'),
            file_name="Company_details.csv",
            mime='text/csv',
        )
    else:
        st.warning("Please paste the data in the text area before extracting.")
