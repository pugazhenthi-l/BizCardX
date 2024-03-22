# main_page.py
import numpy as np
import streamlit as st
import easyocr
import cv2
from PIL import Image
import mysql.connector 
import re

def app():
    st.title('Capture & Create')

    # widget to upload image
    uploaded_file = st.file_uploader("Upload a Business Card", type=["png", "jpg", "jpeg"])

    # Function to read text from image using easyocr
    def extract_text_from_image(image):
        reader = easyocr.Reader(['en'])
        # Convert to grayscale
        gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        # Apply Gaussian blur
        blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
        results = reader.readtext(blurred_image)
        return results


    def create_database():
        conn = mysql.connector.connect(  # Changed to use MySQL connector
            host="127.0.0.1",
            user="root",
            password="root",
            database="bizcardx"
        )
        c = conn.cursor()


        c.execute('''CREATE TABLE IF NOT EXISTS cards (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255),
                        designation VARCHAR(255),
                        company VARCHAR(255),
                        phone VARCHAR(255),
                        email VARCHAR(255),
                        website VARCHAR(255),
                        address TEXT)''')  # Adjusted data types for MySQL
        conn.commit()
        conn.close()

    create_database()








    # Function to calculate the size of the text in the image based on its bounding box
    def get_text_size(bounding_box):
        top_left, top_right, bottom_right, bottom_left = bounding_box
        width = top_right[0] - top_left[0]
        height = bottom_right[1] - top_right[1]
        return width * height

    # Function to find the largest text in the OCR results, used for extracting company name
    def find_largest_text(ocr_results):
        large_text_fraction = 0.53  # threshold to consider the text as large ( used to find company name)

        # Find the largest text size
        max_size = max(get_text_size(result[0]) for result in ocr_results)

        # List to hold large texts in their original order
        large_texts_in_order = []

        for result in ocr_results:
            text = result[1]
            text_size = get_text_size(result[0])

            # Check if the text size is larger than the fraction of the largest text
            if text_size >= max_size * large_text_fraction:
                large_texts_in_order.append(text)

        # Join them to form the company name, preserving the original order
        company_name = ' '.join(large_texts_in_order)
        return company_name

    # Function to categorize extracted text into different fields like company, email, etc.
    def categorize_text(ocr_results):
        data = {
            "company_name": find_largest_text(ocr_results),
            "card_holder": "",
            "designation": "",
            "email": "",
            "phone": [],  # Initialize as an empty list
            "website": "",
            "address": ""
        }
        # Regular expression pattern to identify phone numbers
        phone_pattern = re.compile(r"(\+\d{3}-\d{3}-\d{4}|\d{3}-\d{3}-\d{4})")
        address_lines = []

        for i, result in enumerate(ocr_results):
            text = result[1]
            text_lower = text.lower()

            if phone_pattern.match(text):
                data["phone"].append(text)
            elif "@" in text_lower and not data["email"]:
                data["email"] = text
            elif "www" in text_lower or "http" in text_lower and not data["website"]:
                data["website"] = text_lower
            elif i == 0:
                data["card_holder"] = text
                continue  # Skip adding card holder to the address
            elif i == 1:
                data["designation"] = text
                continue  # Skip adding designation to the address
            elif text in data["company_name"]:
                continue  # Skip adding company name to the address
            else:
                address_lines.append(text)

        # Convert the list of phone numbers to a string AFTER deduplication
        data["phone"] = ', '.join(set(data["phone"]))
        # Join address lines to form a single address string
        data["address"] = ' '.join(address_lines)
        return data

    # Function to insert extracted and categorized data into the database
    def insert_data(name, designation, company, phone, email, website, address):
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            database="bizcardx"
        )
        c = conn.cursor()

        # Query to check if a record already exists with the same name, phone, and email
        check_query = '''SELECT COUNT(*) FROM cards 
                        WHERE name = %s AND phone = %s AND email = %s'''
        c.execute(check_query, (name, phone, email))
        # Fetch the count of records that match the query
        (record_count,) = c.fetchone()

        # If a record exists, do not insert and show a message
        if record_count > 0:
            conn.close()  # Close the connection since no further action is needed
            return "The data already exists."

        # If no record exists, proceed with insertion
        query = '''INSERT INTO cards (name, designation, company, phone, email, website, address) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)'''
        # Executing the query with the data
        c.execute(query, (name, designation, company, phone, email, website, address))
        conn.commit()
        conn.close()
        return "Data saved successfully!"


    # Extract and display the text
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Business Card.', width=600)
        ocr_results = extract_text_from_image(image)

        categorized_data = categorize_text(ocr_results)

        # Extract and display the data in an editable format
        card_holder = categorized_data["card_holder"]
        designation = categorized_data["designation"]
        company_name = categorized_data["company_name"]
        email = categorized_data["email"]
        phone = (categorized_data["phone"])
        website = categorized_data["website"]
        address = categorized_data["address"]
        # Create an expandable section to display extracted information
        with st.expander("Extracted Information", expanded=True):
            # Create a two-column layout
            col1, col2 = st.columns(2)

            # In the left column, display fields for name, designation, and company
            with col1:
                card_holder = st.text_input("Card Holder", card_holder)
                designation = st.text_input("Designation", designation)
                company_name = st.text_input("Company Name", company_name)

            # In the right column, display fields for email, phone, and website
            with col2:
                email = st.text_input("Email", email)
                phone = st.text_input("Phone", phone)
                website = st.text_input("Website", website)
            # Display a text area for the address in bottom center
            address = st.text_area("Address", address, height=100)

            # Optionally, add a button to confirm the edits
            if st.button('Confirm Edits'):
                # Call the function to insert data into the database
                insert_result = insert_data(card_holder, designation, company_name, phone, email, website, address)
                if insert_result == "Data saved successfully!":
                    st.success(insert_result)
                else:
                    st.error(insert_result)

        # Expandable section to show the full OCR results
        with st.expander("Full OCR Results", expanded=False):
            for result in ocr_results:
                st.write(result[1])
