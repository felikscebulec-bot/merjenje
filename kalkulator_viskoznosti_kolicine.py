import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import streamlit as st

 
def run():
 st.title("to je aplikacija KALKULATOR VISKOZNOSTI IN KOLIČINE")
 st.write("v tem programu vpišete zaključno maso in viskoznost ter program bo izračunal viskoznost in količine dveh surovin")
 st.write("če program ne dela pritisnite na gumb RESETIRAJ MODEL ")
 # ---------- reset button ----------
 if st.button("Resetiraj model"):
    if "model" in st.session_state:
        del st.session_state["model"]
    st.success("Model je bil resetiran.")
 
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


    X = df[[found["w"], found["z"]]].values

    y = df[[found["p1"], found["p2"], found["x1"], found["x2"],found["y1"],found["y2"]]].values

    return X, y

 # ---------- excel----------
 X, y = load_data("TRENDI_viskoznosti.xlsx")

 # ---------- trian, test ----------
 X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

 # ----------  Random Forest ----------
 model = RandomForestRegressor(n_estimators=300, random_state=42)
 model.fit(X_train, y_train)

 # ---------- preverja pravilnost ----------
 if "model" not in st.session_state:
    y_pred = model.predict(X_test)
    print("\nModel performance:")
    print(f"R² score: {r2_score(y_test, y_pred):.4f}")
    print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred):.4f}")

    st.session_state.model=model
 else:
        st.info("model je biu ze treniran")
        model=st.session_state.model

    
 w = st.number_input("Vnesite zaključno težo izdelka(kg):", min_value=0, step=1, key="zakljucna_teza", format="%d")
 z = st.number_input("Vnesite zaključno viskoznost izdelka:", min_value=0, step=1, key="zakljucna_viskoznost", format="%d")


 if st.button("Izračunaj", key="kolicina_napoved"):
    X_new_scaled =np.array([[w, z]])
    pred_scaled = model.predict(X_new_scaled)[0]

    p1,p2,x1,x2,y1,y2 = pred_scaled

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


