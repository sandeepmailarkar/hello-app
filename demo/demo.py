import streamlit as st

# Add custom CSS
st.markdown("""
    <style>
        body {
            background-color: #f0f0f0; # Change the background color
        }
        h2 {
            color: #007bff; # Change the color of subheaders
            font-weight: bold; # Make subheaders bold
        }
    </style>
    """, unsafe_allow_html=True)

# Display a title
st.title('My Website')

# Display a subtitle
st.subheader('About Me')

# Display a text
st.write('Hello! I am [Sandeep], a [Coding]. I am passionate about [Dance].')

# Display an image
#st.image('path/to/your/photo.jpg', caption='This is me!', use_column_width=True)

# Display education details
st.subheader('Education')
st.write('- Bachelor of Science in [Your Major], [Your University], [Year]')
st.write('- Master of Science in [Your Major], [Your University], [Year]')

# Display skills
st.subheader('Skills')
st.write('- Python')
st.write('- Data Science')
st.write('- Machine Learning')
