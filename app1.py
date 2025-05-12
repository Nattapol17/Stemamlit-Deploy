import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from datetime import datetime
import datetime as dt
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Automated inventory model", layout="centered")
tab1, tab2, tab3, tab4  = st.tabs(["🏠 Home", "📊 Inventory Forecasting", "🖥️ Inventory Status", "📋 Inventory Track"])
with tab1:
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>📦 Automated inventory model Web App</h1>", unsafe_allow_html=True)
    st.image("ปก.jpg", use_container_width=True)
with tab2:
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>🔍 Inventory Forecasting</h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ Excel (.xlsm หรือ .xlsx)", type=["xlsm", "xlsx"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df['Date'] = pd.to_datetime(df['Date'])
            today = datetime.today()
            df = df[df['Date'] <= today]
            group_col = 'ID' 
            df = df.groupby([group_col, 'Date'], as_index=False)['Quantity'].sum()
          
            for name, group in df.groupby(group_col):
                group = group.dropna(subset=['Date', 'Quantity'])
                if len(group) < 3:
                    st.warning(f"⚠️ Not enough data to fit curve for Item: {name}")
                    continue
                start_date = group['Date'].min()
                group = group.copy()
                group['days'] = (group['Date'] - start_date).dt.days
                xdata = group['days'].values
                ydata = group['Quantity'].values
                try:
                    degree = 2  # ลองใช้ polynomial อันดับ 2 (สามารถเปลี่ยนเป็น 3 หรือมากกว่านี้ได้)
                    coeffs = np.polyfit(xdata, ydata, degree)
                    poly = np.poly1d(coeffs)
                    next_day = group['days'].max() + 1
                    predicted = max(poly(next_day), 0)
                    predicted = round(predicted)

                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.scatter(xdata, ydata, s=10, label='Actual Data')
                    ax.plot(xdata, poly(xdata), 'r-', label='Curve Fit')
                    ax.axvline(next_day, linestyle='--', color='gray', label=f'Day {next_day}')
                    ax.legend()
                    ax.grid(True)
                    ax.set_title(f'ID: {name} – Predicted: {predicted}')
                    ax.set_xlabel(f'Days since {start_date.strftime("%Y-%m-%d")}')
                    ax.set_ylabel("Quantity")
                    st.pyplot(fig)
                    st.success(f"📅 Predicted next-day inventory for **{name}**: `{predicted}`")
                    st.caption("🧠 Polynomial Coefficients → " + ", ".join([f"{c:.3f}" for c in coeffs]))
                except Exception as e:
                    st.error(f"❌ Error fitting data for {name}: {e}")
        except Exception as e:
            st.error(f"❌ ไม่สามารถอ่านไฟล์: {e}")
with tab4:
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>🏷️ Inventory Track</h1>", unsafe_allow_html=True)
with tab3:
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>🏭 Inventory Status</h1>", unsafe_allow_html=True)
    st_autorefresh(interval=2000, key="datarefresh")
    url = 'https://proud-lines-bet.loca.lt/data'
    def led_indicator(value):
        if value == 1:
            color = "red"
        elif value == 0:
            color = "green"
        else:
            color = "gray"
        html = f"""
        <div style="
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: {color};
            display: inline-block;
            border: 2px solid #ccc;
            margin: 5px;
        "></div>
        """
        return html

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            cols = st.columns(6)
            for i in range(6):
                storage_key = f"storage{i+1}"
                value = data.get(storage_key, None)
                color_led = led_indicator(value)
                with cols[i]:
                    st.markdown(f"**storage {i+1}**", unsafe_allow_html=True)
                    st.markdown(color_led, unsafe_allow_html=True)
        else:
            st.error(f"เชื่อมต่อ Node-RED ไม่ได้: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
        


