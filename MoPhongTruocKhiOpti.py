import numpy as np
import matplotlib.pyplot as plt

def hybrid_system_simulation():
    # User input for simulation parameters
    R0 = float(input("Nhập điện trở nội của pin (Ohm): "))
    Voc = float(input("Nhập điện áp hở mạch của pin (Volt): "))
    dung_luong_pin = float(input("Nhập dung lượng pin (Ah): "))
    T = float(input("Nhập nhiệt độ (K): "))
    gia_nhien_lieu_moi_kwh = float(input("Nhập giá nhiên liệu LNG trên mỗi kWh ($): "))
    he_so_phat_thai_CO2 = float(input("Nhập hệ số phát thải CO2 (kg CO2e mỗi kWh): "))
    he_so_phat_thai_NOx = float(input("Nhập hệ số phát thải NOx (kg NOx mỗi kWh): "))
    so_buoc = int(input("Nhập số bước mô phỏng: "))
    soc_start = float(input("Nhập trạng thái sạc ban đầu (SOC, từ 0 đến 1): "))
    soh_start = float(input("Nhập trạng thái sức khỏe ban đầu (SOH, từ 0 đến 1): "))

    # Initial conditions
    soc = soc_start
    soh = soh_start
    tong_phat_thai_CO2 = 0.0
    tong_phat_thai_NOx = 0.0
    tong_chi_phi = 0.0

    # History logs
    lich_su_soc, lich_su_soh = [], []
    lich_su_phat_thai_CO2, lich_su_phat_thai_NOx, lich_su_chi_phi = [], [], []

    # Simulation loop
    for t in range(so_buoc):
        # Calculate power demand (example sinusoidal function)
        P_demand = 10 + 40 * np.sin(2 * np.pi * t / so_buoc)

        # Allocate power between LNG and battery (simple heuristic)
        if soc > 0.2:  # Use battery primarily if SOC > 20%
            P_pin = min(P_demand * 0.7, soc * dung_luong_pin * Voc)
            P_LNG = P_demand - P_pin
        else:  # Use LNG primarily if SOC <= 20%
            P_pin = 0
            P_LNG = P_demand

        # Calculate SOC and SOH changes
        I_pin = P_pin / Voc
        delta_soc = -I_pin / dung_luong_pin
        soc += delta_soc
        soc = max(0, min(1, soc))  # Keep SOC in [0, 1]

        delta_soh = -1e-5 * np.exp(-(1000 + 0.5 * abs(I_pin)) / (8.314 * T)) * (abs(I_pin) ** 1.1)
        soh += delta_soh
        soh = max(0, soh)  # Keep SOH >= 0

        # Calculate emissions and cost
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

    # Print final results
    print("\nKết quả cuối cùng:")
    print(f"Trạng thái sạc cuối cùng (SOC): {soc:.2f}")
    print(f"Trạng thái sức khỏe cuối cùng (SOH): {soh:.2f}")
    print(f"Tổng lượng phát thải CO2 (kg CO2e): {tong_phat_thai_CO2:.2f}")
    print(f"Tổng lượng phát thải NOx (kg NOx): {tong_phat_thai_NOx:.2f}")
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
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(lich_su_chi_phi, label="Tổng chi phí ($)", color="blue")
    plt.title("Tổng chi phí")
    plt.xlabel("Bước thời gian")
    plt.ylabel("Chi phí ($)")
    plt.legend()

    plt.tight_layout()
    plt.show()

# Run simulation
hybrid_system_simulation()
