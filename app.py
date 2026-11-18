import math

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


st.set_page_config(page_title="Pręt paliwowy — rozkład temperatury", page_icon="🌡️", layout="wide")
st.title("Rozkład temperatury w pręcie paliwowym")


with st.sidebar:
    st.header("Parametry pręta i materiałów")
    st.caption("Parametry ustawiono według tabel. λp przyjęto jako 3,5 W/(m·K), w podanym zakresie 2,5–4,5.")
    a = st.number_input("Promień pastylki paliwowej a [m]", min_value=1e-9, value=0.004095, format="%.6g")
    b = st.number_input("Grubość koszulki b [m]", min_value=1e-9, value=0.00057, format="%.6g")
    H = st.number_input("Długość aktywna H [m]", min_value=1e-9, value=4.267, format="%.6g")
    He = st.number_input("Długość ekstrapolowana He [m]", min_value=1e-9, value=4.79, format="%.6g")
    Qpm = st.number_input("Maksymalna gęstość mocy Qpm [W/m³]", min_value=1e-9, value=5.06e8, format="%.6g")
    lambda_p = st.number_input("Przewodność cieplna paliwa λp [W/(m·K)]", min_value=1e-9, value=3.5, format="%.6g")
    lambda_k = st.number_input("Przewodność cieplna koszulki λk [W/(m·K)]", min_value=1e-9, value=17.0, format="%.6g")
    alpha = st.number_input("Współczynnik przejmowania ciepła α [W/(m²·K)]", min_value=1e-9, value=33665.0, format="%.6g")
    st.header("Chłodziwo")
    Tc1 = st.number_input("Temperatura chłodziwa Tc1 przy z = −H/2 [K]", value=552.59, format="%.6g")
    st.caption("G oznacza strumień masy w modelowanym kanale. Wartość całkowita z tabeli wymaga podziału przez liczbę kanałów.")
    G = st.number_input("Strumień masy chłodziwa G [kg/s]", min_value=1e-9, value=0.345, format="%.6g")
    cp = st.number_input("Ciepło właściwe chłodziwa cp [J/(kg·K)]", min_value=1e-9, value=5545.48, format="%.6g")

if He < H:
    st.error("Długość ekstrapolowana He powinna być większa lub równa długości aktywnej H.")
    st.stop()

perimeter = 2.0 * math.pi * (a + b)  # obwód zewnętrzny A
q_m = Qpm * a**2 / (2.0 * (a + b))  # maksymalna gęstość strumienia ciepła


def power_density(z):
    return Qpm * np.cos(np.pi * z / He)


def heat_flux(z):
    return q_m * np.cos(np.pi * z / He)


def coolant_temperature(z):
    return Tc1 + perimeter * q_m * He / (np.pi * G * cp) * (
        np.sin(np.pi * z / He) + np.sin(np.pi * H / (2.0 * He))
    )


def cladding_outer_temperature(z):
    return coolant_temperature(z) + heat_flux(z) / alpha


def cladding_temperature(r, z):
    return cladding_outer_temperature(z) - power_density(z) * a**2 / (2.0 * lambda_k) * np.log(r / (a + b))


def fuel_temperature(r, z):
    return (
        cladding_outer_temperature(z)
        + power_density(z) * a**2 / (4.0 * lambda_p)
        * (1.0 - 2.0 * lambda_p / lambda_k * np.log(a / (a + b)))
        - power_density(z) * r**2 / (4.0 * lambda_p)
    )


tab_radial, tab_axial = st.tabs(["Temperatura promieniowa", "Rozkład osiowy"])

with tab_radial:
    z = st.number_input(
        "Poziom osiowy z dla profilu promieniowego [m]",
        min_value=-He / 2.0,
        max_value=He / 2.0,
        value=0.0,
        format="%.6g",
        help="Zakres wynika z kosinusowego rozkładu mocy Qp(z).",
    )
    st.subheader(f"Temperatura w funkcji promienia dla z = {z:.4g} m")
    r_fuel = np.linspace(0.0, a, 180)
    r_clad = np.linspace(a, a + b, 100)
    fuel_values = fuel_temperature(r_fuel, z)
    clad_values = cladding_temperature(r_clad, z)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(r_fuel, fuel_values, color="#c43c35", label="Paliwo $T_p(r)$")
    ax.plot(r_clad, clad_values, color="#2457a7", label="Koszulka $T_k(r)$")
    ax.axvline(a, color="#667085", linestyle="--", linewidth=1, label="Granica paliwo–koszulka")
    ax.set_xlabel("Promień r [m]")
    ax.set_ylabel("Temperatura [K]")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)

    c1, c2, c3 = st.columns(3)
    c1.metric("Gęstość mocy Qp(z)", f"{power_density(z):,.4g} W/m³")
    c2.metric("Temperatura w osi paliwa", f"{fuel_temperature(0.0, z):,.2f} K")
    c3.metric("Temperatura chłodziwa Tc(z)", f"{coolant_temperature(z):,.2f} K")
    st.caption(
        "Paliwo: równanie (9). Koszulka: równanie (10). Temperaturę zewnętrznej powierzchni koszulki "
        "wyznaczono z warunku konwekcji Tko(z) = Tc(z) + q(z)/α."
    )

with tab_axial:
    z_values = np.linspace(-H / 2.0, H / 2.0, 300)
    q_values = power_density(z_values)
    tc_values = coolant_temperature(z_values)
    tko_values = cladding_outer_temperature(z_values)
    tp1_values = fuel_temperature(a, z_values)
    tpm_values = fuel_temperature(0.0, z_values)

    st.subheader("Osiowy rozkład gęstości mocy")
    fig_power, ax_power = plt.subplots(figsize=(9, 3.5))
    ax_power.plot(z_values, q_values, color="#d88712", label="$Q_p(z)$")
    ax_power.set_xlabel("Współrzędna osiowa z [m]")
    ax_power.set_ylabel("Gęstość mocy [W/m³]")
    ax_power.grid(True, alpha=0.25)
    ax_power.legend()
    fig_power.tight_layout()
    st.pyplot(fig_power, width="stretch")
    plt.close(fig_power)

    st.subheader("Osiowy rozkład temperatur")
    fig_temp, ax_temp = plt.subplots(figsize=(9, 4.2))
    ax_temp.plot(z_values, tc_values, label="Chłodziwo $T_c(z)$", color="#2457a7")
    ax_temp.plot(z_values, tko_values, label="Zewnętrzna powierzchnia koszulki $T_{ko}(z)$", color="#16834a")
    ax_temp.plot(z_values, tp1_values, label="Paliwo na styku z koszulką $T_{p1}(z)$", color="#d88712")
    ax_temp.plot(z_values, tpm_values, label="Oś paliwa $T_{pm}(z)$", color="#c43c35")
    ax_temp.set_xlabel("Współrzędna osiowa z [m]")
    ax_temp.set_ylabel("Temperatura [K]")
    ax_temp.grid(True, alpha=0.25)
    ax_temp.legend()
    fig_temp.tight_layout()
    st.pyplot(fig_temp, width="stretch")
    plt.close(fig_temp)

    mid1, mid2, mid3 = st.columns(3)
    mid1.metric("Maksymalna gęstość mocy Qpm", f"{Qpm:,.4g} W/m³")
    mid2.metric("Maksymalny strumień ciepła qm", f"{q_m:,.4g} W/m²")
    mid3.metric("Temperatura paliwa na styku z koszulką w z = 0", f"{fuel_temperature(a, 0.0):,.2f} K")
    st.caption(
        "Qp(z) = Qpm cos(πz/He), q(z) = qm cos(πz/He), qm = Qpm·a²/[2(a+b)]. "
        "Temperatura chłodziwa wynika z równania (20), temperatura zewnętrznej powierzchni koszulki z (21), "
        "a temperatura osi paliwa z równania (9) dla r = 0. Wykresy pokazują zakres aktywny −H/2 ≤ z ≤ H/2."
    )
