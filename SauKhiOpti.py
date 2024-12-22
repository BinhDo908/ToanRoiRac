import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def hybrid_system_simulation_optimized():
    # Fixed parameters from the article
    R0 = 0.01  # Internal resistance of the battery (Ohm)
    Voc = 3.7  # Open-circuit voltage of the battery (Volt)
    dung_luong_pin = 100  # Battery capacity (Ah)
    T = 298  # Temperature (K)
    gia_nhien_lieu_moi_kwh = 0.1  # LNG fuel cost per kWh ($)
    he_so_phat_thai_CO2 = 0.5  # CO2 emission factor (kg CO2e per kWh)

    # User-defined parameters
    so_buoc = int(input("Nhập số bước mô phỏng: "))
    time_per_step = float(input("Nhập thời gian mỗi bước (giây): "))
    soc_start = float(input("Nhập trạng thái sạc ban đầu (SOC, từ 0 đến 1): "))
    soh_start = float(input("Nhập trạng thái sức khỏe ban đầu (SOH, từ 0 đến 1): "))

    # Initial conditions
    soc = soc_start
    soh = soh_start
    tong_phat_thai_CO2 = 0.0
    tong_chi_phi = 0.0

    # Logs for plotting
    lich_su_soc, lich_su_soh, lich_su_phat_thai_CO2, lich_su_chi_phi = [], [], [], []

    # Function to calculate battery degradation (optimized)
    def calculate_degradation(I_pin):
        delta_soc = -I_pin / dung_luong_pin
        delta_soh = -1e-4 * np.exp(-(1000 + 0.5 * abs(I_pin)) / (8.314 * T)) * (abs(I_pin) ** 1.1)
        return delta_soc, delta_soh

    # Cost function for optimization
    def mpc_cost(u, soc, soh, P_demand):
        P_LNG, P_pin = u

        if P_LNG + P_pin < P_demand:
            return 1e6  # Penalize unmet demand

        I_pin = P_pin / Voc
        delta_soc, delta_soh = calculate_degradation(I_pin)

        fuel_cost = P_LNG * gia_nhien_lieu_moi_kwh * (time_per_step / 3600)
        co2_cost = P_LNG * he_so_phat_thai_CO2 * (time_per_step / 3600)
        soh_penalty = max(0, -delta_soh) * 500  # Higher penalty for SOH degradation
        soc_penalty = max(0, 0.1 - soc) * 1000  # High penalty for low SOC

        return fuel_cost + co2_cost + soh_penalty + soc_penalty

    # Simulation loop
    for t in range(so_buoc):
        # Calculate power demand
        P_demand = max(0, 10 + 40 * np.sin(2 * np.pi * t / so_buoc))

        # Solve optimization problem
        res = minimize(
            mpc_cost,
            x0=[P_demand * 0.5, P_demand * 0.5],
            args=(soc, soh, P_demand),
            bounds=[(0, P_demand * 0.5), (0, P_demand * 0.9)]
        )

        P_LNG, P_pin = res.x if res.success else (P_demand, 0)

        # Calculate battery usage
        I_pin = P_pin / Voc
        delta_soc, delta_soh = calculate_degradation(I_pin)

        # Update SOC and SOH
        soc += delta_soc
        soc = max(0, min(1, soc))
        soh += delta_soh
        soh = max(0, soh)

        # Calculate emissions and cost
        energy_consumed = P_LNG * (time_per_step / 3600)
        chi_phi_nhien_lieu = energy_consumed * gia_nhien_lieu_moi_kwh
        phat_thai_CO2 = energy_consumed * he_so_phat_thai_CO2

        tong_chi_phi += chi_phi_nhien_lieu
        tong_phat_thai_CO2 += phat_thai_CO2

        # Log history
        lich_su_soc.append(soc)
        lich_su_soh.append(soh)
        lich_su_phat_thai_CO2.append(tong_phat_thai_CO2)
        lich_su_chi_phi.append(tong_chi_phi)

    # Print final results
    print("\nKết quả tối ưu hóa:")
    print(f"Tổng thời gian mô phỏng: {so_buoc * time_per_step / 3600:.2f} giờ")
    print(f"Trạng thái sạc cuối cùng (SOC): {soc:.2f}")
    print(f"Trạng thái sức khỏe cuối cùng (SOH): {soh:.2f}")
    print(f"Tổng lượng phát thải CO2 (kg CO2e): {tong_phat_thai_CO2:.2f}")
    print(f"Tổng chi phí vận hành ($): {tong_chi_phi:.2f}")

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
    plt.ylim(0, 8000)  # Adjust scale
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(lich_su_chi_phi, label="Tổng chi phí ($)", color="blue")
    plt.title("Tổng chi phí")
    plt.xlabel("Bước thời gian")
    plt.ylabel("Chi phí ($)")
    plt.ylim(0, 1750)  # Adjust scale
    plt.legend()

    plt.tight_layout()
    plt.show()

# Run the simulation
hybrid_system_simulation_optimized()
