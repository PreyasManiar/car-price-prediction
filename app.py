import streamlit as st
import mysql.connector
import pandas as pd
import pickle as pk

# ✅ Function to connect to MySQL database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="pm5423",  # Replace with your actual password
        database="user_auth"
    )

# ✅ Function to create the users table (if it doesn't exist)
def create_user_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ✅ Function to handle user signup
def signup():
    st.title("Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        conn = connect_db()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            st.error("Username already exists! Please try a different one.")
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            st.success("Signup successful! Please go to the login page.")

        conn.close()

# ✅ Function to handle user login
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            st.success(f"Welcome {username}! Redirecting to Car Price Prediction...")
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["menu"] = "Car Price Prediction"  # Set menu to redirect
            st.rerun()  # Refresh page
        else:
            st.error("Invalid Username or Password.")

        conn.close()

# ✅ Function for car price prediction page
def car_price_prediction():
    st.title("Car Price Prediction")

    # Load trained model
    try:
        model = pk.load(open('model.pkl', 'rb'))
    except FileNotFoundError:
        st.error("Model file not found! Please check 'model.pkl' path.")
        return

    # Load dataset
    try:
        cars_data = pd.read_csv('Cardetails.csv')
        cars_data['brand'] = cars_data['name'].apply(lambda x: x.split(' ')[0])
        cars_data['model'] = cars_data['name'].apply(lambda x: ' '.join(x.split(' ')[1:]))
        cars_data = cars_data.drop_duplicates(subset=['brand', 'model'])
    except FileNotFoundError:
        st.error("Car details dataset not found! Please check 'Cardetails.csv' path.")
        return

    # User Inputs
    brand = st.selectbox("Select Car Brand", cars_data['brand'].unique())
    model_name = st.selectbox("Select Car Model", cars_data[cars_data['brand'] == brand]['model'].unique())
    year = st.slider('Car Manufactured Year', 1994, 2025)
    km_driven = st.slider('Number of km Driven', 10, 1000000)
    fuel = st.selectbox("Select Fuel Type", cars_data['fuel'].unique())
    seller_type = st.selectbox("Select Seller Type", cars_data['seller_type'].unique())
    transmission = st.selectbox("Select Transmission Type", cars_data['transmission'].unique())
    owner = st.selectbox('Owner Type', cars_data['owner'].unique())
    mileage = st.slider('Select Car Mileage', 1, 50)
    engine = st.slider('Engine Size (CC)', 700, 5000)
    max_power = st.slider('Max Power', 0, 500)
    seats = st.slider('Number of seats', 1, 9)

    if st.button("Predict"):
        car_name = f"{brand} {model_name}"
        input_data = pd.DataFrame([[car_name, year, km_driven, fuel, seller_type, transmission, owner, mileage, engine, max_power, seats]],
                                  columns=['name', 'year', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner', 'mileage', 'engine', 'max_power', 'seats'])
        
        # Encoding categorical variables
        input_data['owner'].replace(['First Owner', 'Second Owner', 'Third Owner', 'Fourth & Above Owner', 'Test Drive Car'], [1, 2, 3, 4, 5], inplace=True)
        input_data['fuel'].replace(['Diesel', 'Petrol', 'LPG', 'CNG'], [1, 2, 3, 4], inplace=True)
        input_data['seller_type'].replace(['Individual', 'Dealer', 'Trustmark Dealer'], [1, 2, 3], inplace=True)
        input_data['transmission'].replace(['Manual', 'Automatic'], [1, 2], inplace=True)
        input_data['name'].replace(cars_data['name'].unique(), range(1, len(cars_data['name'].unique()) + 1), inplace=True)

        # Predict price
        car_price = model.predict(input_data)
        st.success(f'Estimated Car Price: ₹{car_price[0]:,.2f}')

# ✅ Main App Navigation
def main():
    create_user_table()  # Ensure user table is created

    # Check session state for automatic redirection
    if "menu" not in st.session_state:
        st.session_state["menu"] = "Login"  # Default menu

    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Go to", ["Sign Up", "Login", "Car Price Prediction", "Logout"], index=["Sign Up", "Login", "Car Price Prediction", "Logout"].index(st.session_state["menu"]))

    if menu == "Sign Up":
        signup()
        st.session_state["menu"] = "Sign Up"
    elif menu == "Login":
        login()
        st.session_state["menu"] = "Login"
    elif menu == "Car Price Prediction":
        if st.session_state.get("logged_in"):
            car_price_prediction()
            st.session_state["menu"] = "Car Price Prediction"
        else:
            st.warning("Please login first!")
    elif menu == "Logout":
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["menu"] = "Login"
        st.success("Logged out successfully!")
        st.rerun()  # Refresh page

# ✅ Corrected entry point
if __name__ == "__main__":
    main()
