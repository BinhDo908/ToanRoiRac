library(ggplot2)
library(dplyr)
library(tidyr)

# Tạo dữ liệu giả lập
steps <- 100
time <- seq(1, steps)

# Hiện trạng ban đầu (chưa tối ưu)
SOC <- c(seq(1, 0.1, length.out = 20), rep(0, 80))
SOH <- c(seq(1, 0.995, length.out = 40), rep(0.994, 60))
CO2 <- cumsum(c(rep(5, 20), rep(8, 80))) # Tăng nhanh do LNG chiếm phần lớn
Cost <- cumsum(c(rep(1, 20), rep(2, 80))) # Chi phí tăng mạnh

# Cải tiến (sau tối ưu hóa)
SOC_optimized <- c(seq(1, 0.2, length.out = 50), rep(0.2, 50)) # SOC giữ ổn định ở mức tối thiểu
SOH_optimized <- c(seq(1, 0.998, length.out = 50), rep(0.998, 50)) # SOH giảm nhẹ
CO2_optimized <- cumsum(c(rep(3, 50), rep(5, 50))) # Phát thải giảm nhờ tối ưu LNG
Cost_optimized <- cumsum(c(rep(0.5, 50), rep(1, 50))) # Chi phí giảm đáng kể

# Kết hợp dữ liệu
data <- data.frame(
  Time = rep(time, 2),
  SOC = c(SOC, SOC_optimized),
  SOH = c(SOH, SOH_optimized),
  CO2 = c(CO2, CO2_optimized),
  Cost = c(Cost, Cost_optimized),
  Type = rep(c("Baseline", "Optimized"), each = steps)
)

# Tái cấu trúc dữ liệu cho tất cả các trạng thái
data_long <- data %>%
  pivot_longer(cols = c(SOC, SOH, CO2, Cost), names_to = "Variable", values_to = "Value")

# Vẽ biểu đồ toàn diện
ggplot(data_long, aes(x = Time, y = Value, color = Type)) +
  geom_line(size = 1.2) +
  facet_wrap(~Variable, scales = "free_y", ncol = 2) +
  labs(title = "So sánh trạng thái hệ thống (Baseline vs Optimized)",
       x = "Thời gian (bước)",
       y = "Giá trị trạng thái") +
  theme_minimal() +
  theme(
    axis.title.x = element_text(size = 14, face = "bold"),
    axis.title.y = element_text(size = 14, face = "bold"),
    strip.text = element_text(size = 12, face = "bold"),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 10)
  )
