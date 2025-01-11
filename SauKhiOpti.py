import numpy as np
import matplotlib.pyplot as plt

def hybrid_system_simulation():
    # Default parameters from the image
    R0 = 0.01  # Điện trở nội của pin (Ohm)
    Voc = 3.7  # Điện áp hở mạch của pin (Volt)
    dung_luong_pin = 100  # Dung lượng pin (Ah)
    T = 298  # Nhiệt độ (K)
    gia_nhien_lieu_moi_kwh = 0.1  # Giá nhiên liệu LNG trên mỗi kWh ($)
    he_so_phat_thai_CO2 = 0.5  # Hệ số phát thải CO2 (kg CO2e mỗi kWh)
    he_so_phat_thai_NOx = 0.02  # Hệ số phát thải NOx (kg NOx mỗi kWh)
    chi_phi_suy_giam_pin_moi_ah = 0.045  # Chi phí suy giảm pin trên mỗi Ah ($)
    chi_phi_phat_thai_CO2e = 0.02  # Chi phí khí thải CO2e trên mỗi kg ($)
    so_buoc = 100  # Số bước mô phỏng
    thoi_gian_moi_buoc = 3600  # Thời gian mỗi bước (giây)
    soc_start = 0.9  # Trạng thái sạc ban đầu (SOC)
    soh_start = 0.95  # Trạng thái sức khỏe ban đầu (SOH)

    # Optimization weights
    soc_min = 0.3
    soc_max = 0.85
    lng_efficiency = 0.87

    # Initial conditions
    soc = soc_start
    soh = soh_start
    total_co2_emissions = 0.0
    total_nox_emissions = 0.0
    total_cost = 0.0
    total_lcc = 0.0

    # History logs
    soc_history = []
    soh_history = []
    co2_emissions_history = []
    nox_emissions_history = []
    cost_history = []
    lcc_history = []

    for t in range(so_buoc):
        # Demand calculation
        power_demand = 10 + 40 * np.sin(2 * np.pi * t / so_buoc)

        # LNG and Battery Allocation
        if soc > soc_min:
            if soc > 0.6:
                power_from_battery = min(power_demand * 0.8, soc * dung_luong_pin * Voc / (thoi_gian_moi_buoc / 3600))
            else:
                power_from_battery = min(power_demand * 0.7, soc * dung_luong_pin * Voc / (thoi_gian_moi_buoc / 3600))
            power_from_lng = power_demand - power_from_battery
        else:
            power_from_battery = 0
            power_from_lng = power_demand

        power_from_lng *= lng_efficiency

        # SOC Update
        battery_current = power_from_battery / Voc
        soc_change = -battery_current * (thoi_gian_moi_buoc / 3600) / dung_luong_pin
        soc += soc_change
        soc = max(soc_min, min(soc_max, soc))

        # SOH Update
        soh_change = -4e-6 * np.exp(-abs(battery_current)) * (abs(battery_current) ** 1.1)
        soh += soh_change
        soh = max(0, soh)

        # Cost Calculations
        fuel_cost = power_from_lng * gia_nhien_lieu_moi_kwh * (thoi_gian_moi_buoc / 3600)
        co2_emissions = power_from_lng * he_so_phat_thai_CO2 * (thoi_gian_moi_buoc / 3600)
        nox_emissions = power_from_lng * he_so_phat_thai_NOx * (thoi_gian_moi_buoc / 3600)
        degradation_cost = abs(battery_current) * (thoi_gian_moi_buoc / 3600) * chi_phi_suy_giam_pin_moi_ah
        co2_cost = co2_emissions * chi_phi_phat_thai_CO2e

        # Update totals
        total_cost += fuel_cost
        total_co2_emissions += co2_emissions
        total_nox_emissions += nox_emissions
        total_lcc += fuel_cost + degradation_cost + co2_cost

        # Log metrics
        soc_history.append(soc)
        soh_history.append(soh)
        co2_emissions_history.append(total_co2_emissions)
        nox_emissions_history.append(total_nox_emissions)
        cost_history.append(total_cost)
        lcc_history.append(total_lcc)

    # Print final results
    print("\nKết quả cuối cùng:")
    print(f"SOC cuối cùng: {soc:.2f}")
    print(f"SOH cuối cùng: {soh:.2f}")
    print(f"Tổng lượng phát thải CO2 (kg CO2e): {total_co2_emissions:.2f}")
    print(f"Tổng lượng phát thải NOx (kg NOx): {total_nox_emissions:.2f}")
    print(f"Tổng chi phí vận hành ($): {total_cost:.2f}")
    print(f"Tổng chi phí vòng đời (LCC) ($): {total_lcc:.2f}")

    # Plot results
    plt.figure(figsize=(15, 10))

    plt.subplot(2, 3, 1)
    plt.plot(soc_history, label="SOC")
    plt.title("Trạng thái sạc (SOC)")
    plt.xlabel("Bước thời gian")
    plt.ylabel("SOC")
    plt.legend()

    plt.subplot(2, 3, 2)
    plt.plot(soh_history, label="SOH", color="orange")
    plt.title("Trạng thái sức khỏe (SOH)")
    plt.xlabel("Bước thời gian")
    plt.ylabel("SOH")
    plt.legend()

    plt.subplot(2, 3, 3)
    plt.plot(co2_emissions_history, label="Tổng lượng phát thải CO2", color="green")
    plt.title("Tổng lượng phát thải CO2 (kg CO2e)")
    plt.xlabel("Bước thời gian")
    plt.ylabel("Phát thải CO2 (kg CO2e)")
    plt.legend()

    plt.subplot(2, 3, 4)
    plt.plot(cost_history, label="Tổng chi phí ($)", color="blue")
    plt.title("Tổng chi phí")
    plt.xlabel("Bước thời gian")
    plt.ylabel("Chi phí ($)")
    plt.legend()

    plt.subplot(2, 3, 5)
    plt.plot(lcc_history, label="Tổng chi phí LCC ($)", color="red")
    plt.title("Tổng chi phí vòng đời (LCC)")
    plt.xlabel("Bước thời gian")
    plt.ylabel("Chi phí LCC ($)")
    plt.legend()

    plt.tight_layout()
    plt.show()

# Run simulation
hybrid_system_simulation()
