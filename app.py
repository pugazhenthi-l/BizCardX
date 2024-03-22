import streamlit as st
import main_page
import edit_page
import export_page

st.set_page_config(page_title="CardCrafter Pro: The Ultimate Business Card Management Suite", page_icon=":card_file_box:", layout="wide")

# Initialize the session state for page navigation if it's not already set
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = None

# Define a function that sets the Streamlit UI and pages without using the sidebar.
def main():
    st.image("guvi.png", width=100)
    st.markdown("""
        <h1 style='text-align: center;'>CardCrafter Pro</h1>
        <h4 style='text-align: center; color: grey;'>The Ultimate Business Card Management Suite</h4>
        """, unsafe_allow_html=True)

    # About Information
    st.markdown("## About")
    st.info(
        '''CardCrafter Pro transforms your business card chaos into an organized digital directory, making networking simple and efficient.
        \n- **Data Capture**: Upload a business card image to start digitizing.
        \n- **Data Manager**: Modify the details of your saved business cards.
        \n- **Data Exporter**: Download your contacts as a CSV file for easy access and sharing.
        \nFor more information or feature requests, connect me on [LinkedIn](https://www.linkedin.com/in/pugazhenthi-l)...'''
    )


    # Pages dictionary
    pages = {
        "Data Capture": main_page,
        "Data Manager": edit_page,
        "Data Exporter": export_page
    }

    # Display buttons for each page in the pages dictionary
    for page_name in pages.keys():
        if st.button(page_name):
            st.session_state['current_page'] = page_name

    # Display the selected page using the session state
    if st.session_state['current_page'] in pages:
        pages[st.session_state['current_page']].app()

if __name__ == "__main__":
    main()
