import streamlit as st

# Display a title
st.title('Hello World App')

# Add a text input field for the user to enter their name
user_name = st.text_input("Enter your name:")

# Add a button that, when clicked, displays a personalized greeting
if st.button('Greet'):
    if user_name:
        st.write(f'Hello, {user_name}!')
    else:
        st.write('Hello, World!')

# Add a range slider for selecting a number between 10 and 90
selected_number = st.slider('Select a number between 10 and 90:', min_value=10, max_value=90, value=50)

# Display a message based on the selected number
if selected_number < 30:
    st.write(f'The number {selected_number} is less than 30.')
elif selected_number < 60:
    st.write(f'The number {selected_number} is between 30 and 60.')
else:
    st.write(f'The number {selected_number} is greater than or equal to 60.')
