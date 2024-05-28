import pandas as pd
import streamlit as st

@st.cache
def load_data():
    data = pd.read_csv(r'C:\Users\Matus\PycharmProjects\PythonDataStructuresAndAlgorithmsCourse\DeltaGreen\Task1.csv', parse_dates=['time'], index_col='time')
    data.columns = ['consumption_power']

    # Converting Watts to Killowats
    data['kW'] = data['consumption_power'] / 1000

    # Grouping by an hour period to get kW/h
    data = data.resample('H').sum()

    return data

data = load_data()

# Display data as a table
st.subheader('Data')
st.write(data)

# Display data as a line chart
st.subheader('Energy consumption (kW/h)')
st.line_chart(data['kW'])

