import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import streamlit as st
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.callbacks import EarlyStopping



def run():
    st.title("To je aplikacija izracun_sestavin")
    st.write("v tem programu vpišete zaključno maso in viskoznost ter program bo izračunal viskoznost in količine dveh surovin")
    st.write("če program ne dela pritisnite na gumb RESETIRAJ MODEL ")
    # ---------- resset ----------
    if st.button("Resetiraj model"):
        if "model" in st.session_state:
            del st.session_state["model"]
        st.success("Model se resetira")
    
    
    def load_data(path: str):
        df = pd.read_excel(path)

        name_map = {
            "Viskoznost sestavine 1": "y1",
            "Viskoznost sestavine 2": "y2",
            "Količina sestavine 1 [kg]": "x1",
            "Količina sestavine 2 [kg]": "x2",
            "Viskoznost izdelka": "z",
            "Teža izdelka [kg]": "w",
            "procenti sestavine 1 [%]": "p1",
            "procenti sestavine 2 [%]": "p2"
        }

        found = {}
        for k, v in name_map.items():
            matches = [c for c in df.columns if c == k]
            if matches:
                found[v] = matches[0]

        required = ["y1", "y2", "z", "w", "p1", "p2"]
        if not all(k in found for k in required):
            st.error("Manjkajo zahtevani stolpci v Excelu.")
            return None, None

        for col in found.values():
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=found.values())

        X = df[[found["z"], found["w"]]].values
        y = df[[ found["p1"], found["p2"], found["y1"], found["y2"],found["x1"],found["x2"]]].values

        return X, y

    # ---------- excel----------
    X, y = load_data("TRENDI_viskoznosti.xlsx")


    #---scaler---
    if "scaler_X" not in st.session_state:
        st.session_state.scaler_X = StandardScaler()
    if "scaler_y" not in st.session_state:
        st.session_state.scaler_y = StandardScaler()

    X_scaled = st.session_state.scaler_X.fit_transform(X)
    y_scaled = st.session_state.scaler_y.fit_transform(y)



    # ---------- x_train x_test ----------
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

    # ---------- nevtronska mreža ----------
    if "model" not in st.session_state:
        st.session_state.model = Sequential([
            Dense(64, input_dim=2, activation='relu'),
            Dense(128, activation='relu'),
            Dense(64, activation='relu'),
            Dense(6)
        ])
        st.session_state.model.compile(optimizer='adam', loss='mse')



        early_stop = EarlyStopping(monitor="val_loss", patience=100, restore_best_weights=True)
        st.session_state.model.fit(X_train, y_train, epochs=500, batch_size=4,
                  validation_data=(X_test, y_test), verbose=0, callbacks=[early_stop])
    else:
        st.info("Model je bil že treniran.")
        model = st.session_state.model
        


    w = st.number_input("Vnesite zaključno težo izdelka(kg):", min_value=0, step=1, key="tezavis_w", format="%d")
    z = st.number_input("Vnesite zaključno viskoznost izdelka:", min_value=0, step=1, key="tezavis_z", format="%d")


    if st.button("Izračunaj", key="tezavis_btn"):
        X_new_scaled = st.session_state.scaler_X.transform(np.array([[z, w]]))
        pred_scaled = st.session_state.model.predict(X_new_scaled)
        pred = st.session_state.scaler_y.inverse_transform(pred_scaled)[0]



        p1, p2, y1, y2, x1, x2 = pred
        if p1 <= 1.0 and p2 <= 1.0:
            p1 *= 100
            p2 *= 100
            x1 = w * (p1 / 100)
            x2 = w * (p2 / 100)




        st.subheader("Predvidena sestava sestavin:")
        st.write(f"**Viskoznost sestavine 1:** {y1:.2f}")
        st.write(f"**Viskoznost sestavine 2:** {y2:.2f}")
        st.write(f"**Količina sestavine 1:** {x1:.2f} kg ({p1:.2f}%)")
        st.write(f"**Količina sestavine 2:** {x2:.2f} kg ({p2:.2f}%)")