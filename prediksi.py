import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from io import BytesIO

# Judul Aplikasi
st.title("Prediksi Hasil Deteksi Data")

# Menu Upload Data
st.header("Upload Data")
uploaded_file = st.file_uploader("Upload file CSV dengan data", type="csv")

# Fungsi untuk Mengunduh Data
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

if uploaded_file is not None:
    # Membaca Data yang Diunggah
    data = pd.read_csv(uploaded_file)
    st.write("Data yang diunggah:")
    st.write(data.head())

    # Memastikan Data Berisi Fitur dan Target (atau Dummy untuk Prediksi)
    st.header("Konfigurasi Model")
    with st.expander("Pengaturan Kolom"):
        features = st.multiselect("Pilih Kolom Fitur", options=data.columns, default=data.columns[:-1])
        target = st.selectbox("Pilih Kolom Target (True/False)", options=data.columns, index=len(data.columns)-1)

    if st.button("Mulai Prediksi"):
        try:
            # Preprocessing Data
            X = data[features]
            y = data[target] if target in data else np.random.choice([0, 1], size=len(data))

            # Membagi Data untuk Training dan Testing
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Membuat Model (RandomForest untuk Simulasi)
            model = RandomForestClassifier(random_state=42)
            model.fit(X_train, y_train)

            # Prediksi Data
            data['Prediction'] = model.predict(X)
            data['Prediction'] = data['Prediction'].apply(lambda x: True if x == 1 else False)

            st.write("Hasil Prediksi:")
            st.write(data.head())

            # Menyediakan Data untuk Diunduh
            csv = convert_df_to_csv(data)
            st.download_button(
                label="Unduh Hasil Prediksi sebagai CSV",
                data=csv,
                file_name="hasil_prediksi.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Harap unggah file CSV untuk memulai.")
