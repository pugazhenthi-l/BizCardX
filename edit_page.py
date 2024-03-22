# edit_page.py
import streamlit as st
import mysql.connector


# MySQL connection details
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root",
    "database": "bizcardx"
}

# Function to fetch data from the database
def fetch_data():
    conn = mysql.connector.connect(**db_config)  # Use MySQL connector with the provided db_config
    c = conn.cursor()
    c.execute("SELECT * FROM cards")  # Fetch all fields
    data = c.fetchall()
    conn.close()
    return data



# Function to update a specific record in the database
def update_data(record_id, name, designation, company, phone, email, website, address):
    conn = mysql.connector.connect(**db_config)  # Use MySQL connector with the provided db_config
    c = conn.cursor()
    query = '''UPDATE cards 
               SET name = %s, designation = %s, company = %s, phone = %s, email = %s, website = %s, address = %s 
               WHERE id = %s'''  
    c.execute(query, (name, designation, company, phone, email, website, address, record_id))
    conn.commit()
    conn.close()

# Function to delete a specific record from the database
def delete_data(record_id):
    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    query = "DELETE FROM cards WHERE id = %s"
    c.execute(query, (record_id,))
    conn.commit()
    conn.close()
    # After successful deletion, rerun the app to refresh the page
    st.experimental_rerun()
    st.query_params()

def app():
    st.title('Share & Export')

    # Fetch and display data
    data = fetch_data()
    if not data:
        st.write("No data found")
        return

    # Create a mapping of company names to IDs
    company_mapping = {row[0]: row[3] for row in data}
    selected_id = st.selectbox("Select a company to edit",
                               list(company_mapping.keys()), format_func=lambda x: company_mapping[x])

    # Find the selected record
    selected_record = next((row for row in data if row[0] == selected_id), None)

    if selected_record:
        new_name = st.text_input("Name", selected_record[1])
        new_designation = st.text_input("Designation", selected_record[2])
        new_company = st.text_input("Company", selected_record[3])
        new_phone = st.text_input("Phone", selected_record[4])
        new_email = st.text_input("Email", selected_record[5])
        new_website = st.text_input("Website", selected_record[6])
        new_address = st.text_input("Address", selected_record[7])

        # Checkbox for delete confirmation
        confirm_delete = st.checkbox("Confirm deletion")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Update Record"):
                update_data(selected_id, new_name, new_designation, new_company, new_phone, new_email, new_website,
                            new_address)
                st.success("Record updated successfully!")

        with col2:
            if st.button("Delete Record", disabled=not confirm_delete):
                delete_data(selected_id)
                st.success("Record deleted successfully!")

#         col1, col2, col3 = st.columns(3)
#         with col1:
#             if st.button("Update Record"):
#                 update_data(selected_id, new_name, new_designation, new_company, new_phone, new_email, new_website,
#                             new_address)
#                 st.success("Record updated successfully!")

#         with col2:
#             if st.button("Delete Record"):
#                 # Show confirmation and cancel buttons
#                 delete_confirmation = st.empty()
#                 confirm_col1, confirm_col2 = delete_confirmation.columns([1, 1])
#                 with confirm_col1:
#                     if st.button("Confirm Delete"):
#                         delete_data(selected_id)
#                         st.success("Record deleted successfully!")
#                 with confirm_col2:
#                     if st.button("Cancel"):
#                         delete_confirmation.empty()  # Remove the confirmation and cancel buttons if cancelled

# # After updating the function definitions and app structure, make sure to call the app function at the end if it's the main module
# if __name__ == "__main__":
#     app()