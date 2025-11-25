import streamlit as st
import izracun_kolicine
import izracun_sestavin
import kalkulator_kolicine
import kalkulator_viskoznosti_kolicine


st.sidebar.title("izberi program ki ga zelite uporabiti")
choice=st.sidebar.radio ( "programi",["izracun_kolicine","izracun_sestavin","kalkulator_kolicine","kalkulator_viskoznosti _kolicine"])
if choice=="izracun_kolicine":
    izracun_kolicine.run()
elif choice=="izracun_sestavin":
    izracun_sestavin.run()
elif choice=="kalkulator_kolicine":
    kalkulator_kolicine.run() 
elif choice=="kalkulator_viskoznosti _kolicine":
    kalkulator_viskoznosti_kolicine.run()



