import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import plotly.express as px




import pandas as pd
import streamlit as st

def load_data():
    data = pd.read_csv(r'Task1.csv', parse_dates=['time'], index_col='time')
    data.columns = ['consumption_power']

    # Converting Watts to Killowats
    data['kW'] = data['consumption_power'] / 1000

    # Grouping by an hour period to get kW/h
    data = data.resample('H').sum()

    return data

menu = st.sidebar.selectbox('Menu', ['Task 1', 'Task 2'])

if menu == 'Task 1':
    data = load_data()

    # Display data as a table
    st.subheader('Data')
    st.write(data[['kW']])

    # Display data as a line chart
    st.subheader('Energy consumption (kW/h)')
    st.line_chart(data['kW'])

if menu == 'Task 2':
    @st.cache
    def load_data():
        data = pd.read_csv(r'Task2.csv')
        data.columns = ['id', 'timestamp', 'control_mode', 'manufacturer', 'battery_capacity']
        return data

    data = load_data()
    devices = data['id'].unique()

    # Include a button for selecting all devices
    if st.button('Select All Devices'):
        selected_devices = devices.tolist()
    else:
        selected_devices = st.multiselect('Select devices', devices)

    filtered_data = data[data['id'].isin(selected_devices)]
    filtered_data['timestamp'] = pd.to_datetime(filtered_data['timestamp'])
    filtered_data['date'] = filtered_data['timestamp'].dt.date

    fig = go.Figure()  # Create figure outside loop

    for device in selected_devices:
        device_data = filtered_data[filtered_data['id'] == device].sort_values('timestamp')

        # Calculate control mode usage statistics
        control_mode_usage = device_data['control_mode'].value_counts(normalize=True) * 100
        control_mode_usage = control_mode_usage.round(2).to_dict()

        # Calculate battery capacity statistics
        average_battery_capacity = device_data['battery_capacity'].mean()
        min_battery_capacity = device_data['battery_capacity'].min()
        max_battery_capacity = device_data['battery_capacity'].max()

        fig.add_trace(go.Scatter(
            x=device_data['timestamp'],
            y=device_data['battery_capacity'],
            mode='lines',
            name=device,
            hovertemplate="<b>ID:</b> "
                          + device
                          + "<br><b>Control Mode:</b> "
                          + device_data['control_mode'].iloc[0]
                          + "<br><b>Manufacturer:</b> "
                          + device_data['manufacturer'].iloc[0]
                          + "<br><b>Timestamp:</b> "
                          + "%{x}<br><b>Battery Capacity:</b> "
                          + "%{y}<br><b>Average Battery Capacity:</b> "
                          + str(round(average_battery_capacity, 2))
                          + "<br><b>Min Battery Capacity:</b> "
                          + str(min_battery_capacity)
                          + "<br><b>Max Battery Capacity:</b> "
                          + str(max_battery_capacity)
                          + "<br><b>Manual Mode Usage:</b> "
                          + str(control_mode_usage.get('MANUAL', 0)) + "%"
                          + "<br><b>Automatic Mode Usage:</b> "
                          + str(control_mode_usage.get('AUTOMATIC', 0)) + "%"
                          + "<extra></extra>"
        ))

    fig.update_layout(height=500, width=700,
                      title_text="Battery Capacity for separate id's",
                      xaxis_title="Timestamp",
                      yaxis_title="Battery Capacity")
    st.plotly_chart(fig)

    # Show battery capacity for each date
    st.subheader('Battery Capacity - Aggregated')

    # Compute additional statistics for each day
    capacity_by_date = filtered_data.groupby('date').agg({
        'battery_capacity': 'sum',
        'control_mode': [lambda x: dict(x.value_counts()), lambda x: x.value_counts().idxmax()],
        'manufacturer': ['nunique', lambda x: dict(x.value_counts()), lambda x: x.value_counts().idxmax()],
        'id': 'nunique'
    }).reset_index()

    # Rename columns
    capacity_by_date.columns = ['date', 'total_capacity', 'modes_count',
                                'most_common_mode', 'num_unique_manufacturers', 'manufacturers_count',
                                'most_common_manufacturer', 'num_unique_ids',
                                ]

    # Convert dictionaries to string
    capacity_by_date['modes_count'] = capacity_by_date['modes_count'].apply(str)
    capacity_by_date['manufacturers_count'] = capacity_by_date['manufacturers_count'].apply(str)

    # Re-adjust other calculations
    capacity_by_date['weekly_capacity'] = (capacity_by_date['total_capacity'] / capacity_by_date['total_capacity'].sum()) * 100
    capacity_by_date['weekly_capacity'] = capacity_by_date['weekly_capacity'].round(2)
    capacity_by_date['daily_change'] = capacity_by_date['total_capacity'].pct_change() * 100
    capacity_by_date['daily_change'] = capacity_by_date['daily_change'].round(2)

    # Update hover_data in plotting
    fig2 = px.line(capacity_by_date, x="date", y="total_capacity",
                   hover_data=["weekly_capacity", "daily_change",
                                'modes_count',
                                 'manufacturers_count', 'most_common_mode',
                                'most_common_manufacturer', 'num_unique_ids'],
                   labels={'weekly_capacity': 'Weekly Capacity %',
                           'daily_change': 'Daily Change %',
                           'modes_count': 'Mode Counts',
                           'manufacturers_count': 'Manufacturer Counts',
                           'most_common_mode': 'Most Common Mode',
                           'most_common_manufacturer': 'Most Common Manufacturer',
                           'num_unique_ids': 'Number of Unique Active IDs'
                           })
    st.plotly_chart(fig2)

    #exclude columns most_common_mode, most_common_manufacturer and modes_count
    capacity_by_date = capacity_by_date.drop(columns=['most_common_mode', 'most_common_manufacturer', 'modes_count', 'num_unique_manufacturers'])

    # Create a table with Streamlit
    st.table(capacity_by_date)