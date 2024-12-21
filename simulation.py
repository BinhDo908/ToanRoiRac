import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Constants
R0 = 0.01  # Internal resistance of the battery (Ohm)
Voc = 3.7  # Open-circuit voltage of the battery (Volt)
dung_luong_pin = 100  # Battery capacity (Ah)
T = 298  # Temperature (K)
R = 8.314  # Ideal gas constant (J/(mol·K))

# Battery degradation model coefficients
A, B, C, D = 1e-5, 1000, 0.5, 1.1

gia_nhien_lieu_moi_kwh = 0.1  # LNG fuel cost per kWh ($)
he_so_phat_thai_CO2 = 0.5  # CO2 emission factor (kg CO2e per kWh)
he_so_phat_thai_NOx = 0.02  # NOx emission factor (kg NOx per kWh)
so_buoc = 100  # Number of simulation steps

# Initial conditions
soc = 1.0  # State of charge (SOC), starting at 100%
soh = 1.0  # State of health (SOH), starting at 100%
tong_phat_thai_CO2 = 0.0  # Total CO2 emissions (kg CO2e)
tong_phat_thai_NOx = 0.0  # Total NOx emissions (kg NOx)
tong_chi_phi = 0.0  # Total cost ($)

# Time-varying power demand (kW)
nhu_cau_cong_suat = 10 + 40 * np.sin(np.linspace(0, 2 * np.pi, so_buoc))

# History logs
lich_su_soc, lich_su_soh = [], []
lich_su_phat_thai_CO2, lich_su_phat_thai_NOx, lich_su_chi_phi = [], [], []

# Extended Kalman Filter (EKF) for power demand prediction
def ekf_predict(state, control, noise_covariance):
    """Predict the next power demand state using EKF."""
    P = state[0]
    dP = 40 * np.cos(control)
    new_P = np.clip(P + dP + np.random.normal(0, noise_covariance), 0, 50)
    return new_P, control + 0.1

state = (nhu_cau_cong_suat[0], 0)  # Initial state: (power demand, control)
noise_cov = 0.5

# Cost function for MPC
def mpc_cost(u, soc, soh, P_demand):
    """Cost function for MPC optimization."""
    P_LNG, P_pin = u
    if P_LNG + P_pin < P_demand:
        return 1e6  # Penalize unmet demand

    I_pin = P_pin / Voc
    delta_soc = -I_pin / dung_luong_pin
    delta_soh = -A * np.exp(-(B + C * abs(I_pin)) / (R * T)) * (abs(I_pin) ** D)

    return (
        gia_nhien_lieu_moi_kwh * P_LNG +  # Fuel cost
        he_so_phat_thai_CO2 * P_LNG +  # CO2 emissions
        he_so_phat_thai_NOx * P_LNG +  # NOx emissions
        abs(delta_soc) * 1e3 +  # Penalize low SOC
        abs(delta_soh) * 1e4    # Penalize SOH degradation
    )

# Simulation loop
for t in range(so_buoc):
    # Predict power demand using EKF
    nhu_cau_cong_suat[t], control = ekf_predict(state, state[1], noise_cov)
    state = (nhu_cau_cong_suat[t], control)

    # Solve MPC optimization
    res = minimize(
        mpc_cost,
        x0=[0.5 * nhu_cau_cong_suat[t], 0.5 * nhu_cau_cong_suat[t]],  # Initial guess
        args=(soc, soh, nhu_cau_cong_suat[t]),
        bounds=[(0, nhu_cau_cong_suat[t]), (0, nhu_cau_cong_suat[t])],
    )

    P_LNG, P_pin = res.x
    I_pin = P_pin / Voc
    delta_soc = -I_pin / dung_luong_pin
    soc += delta_soc
    soc = max(0, min(1, soc))

    delta_soh = -A * np.exp(-(B + C * abs(I_pin)) / (R * T)) * (abs(I_pin) ** D)
    soh += delta_soh
    soh = max(0, soh)

    chi_phi_nhien_lieu = P_LNG * gia_nhien_lieu_moi_kwh
    phat_thai_CO2 = P_LNG * he_so_phat_thai_CO2
    phat_thai_NOx = P_LNG * he_so_phat_thai_NOx

    tong_chi_phi += chi_phi_nhien_lieu
    tong_phat_thai_CO2 += phat_thai_CO2
    tong_phat_thai_NOx += phat_thai_NOx

    # Log history
    lich_su_soc.append(soc)
    lich_su_soh.append(soh)
    lich_su_phat_thai_CO2.append(tong_phat_thai_CO2)
    lich_su_phat_thai_NOx.append(tong_phat_thai_NOx)
    lich_su_chi_phi.append(tong_chi_phi)

# Results
print("SOC cuối cùng:", soc)
print("SOH cuối cùng:", soh)
print("Tổng lượng phát thải CO2 (kg CO2e):", tong_phat_thai_CO2)
print("Tổng lượng phát thải NOx (kg NOx):", tong_phat_thai_NOx)
print("Tổng chi phí ($):", tong_chi_phi)

# Plot results
plt.figure(figsize=(15, 10))

plt.subplot(2, 2, 1)
plt.plot(lich_su_soc, label="SOC")
plt.title("Trạng thái sạc (SOC)")
plt.xlabel("Bước thời gian")
plt.ylabel("SOC")
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(lich_su_soh, label="SOH", color="orange")
plt.title("Trạng thái sức khỏe (SOH)")
plt.xlabel("Bước thời gian")
plt.ylabel("SOH")
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(lich_su_phat_thai_CO2, label="Tổng lượng phát thải CO2", color="green")
plt.title("Tổng lượng phát thải CO2 (kg CO2e)")
plt.xlabel("Bước thời gian")
plt.ylabel("Phát thải CO2 (kg CO2e)")
plt.legend()

plt.subplot(2, 2, 4)
plt.plot(lich_su_chi_phi, label="Tổng chi phí ($)", color="blue")
plt.title("Tổng chi phí")
plt.xlabel("Bước thời gian")
plt.ylabel("Chi phí ($)")
plt.legend()

plt.tight_layout()
plt.show()
