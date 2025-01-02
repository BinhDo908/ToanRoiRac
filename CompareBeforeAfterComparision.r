# Data for the comparison
# Results before optimization
before <- data.frame(
  Metric = c("SOC", "SOH", "CO2 Emissions (kg)", "NOx Emissions (kg)", "Operating Cost ($)"),
  Value = c(0.17, 1.00, 346.52, 13.86, 69.30)
)

# Results after optimization
after <- data.frame(
  Metric = c("SOC", "SOH", "CO2 Emissions (kg)", "NOx Emissions (kg)", "Operating Cost ($)"),
  Value = c(0.26, 1.00, 333.13, 13.33, 66.63)
)

# Combine data for visualization
library(ggplot2)
comparison <- rbind(
  data.frame(before, Status = "Before Optimization"),
  data.frame(after, Status = "After Optimization")
)

# Plotting individual comparisons as bar charts
metrics <- unique(comparison$Metric)
plot_list <- list()

for (metric in metrics) {
  plot <- ggplot(subset(comparison, Metric == metric), aes(x = Status, y = Value, fill = Status)) +
    geom_bar(stat = "identity", position = "dodge") +
    labs(
      title = paste("Comparison for", metric),
      x = "Optimization Status",
      y = metric
    ) +
    theme_minimal()
  plot_list[[metric]] <- plot
}

# Display all plots
library(gridExtra)
grid.arrange(grobs = plot_list, ncol = 2)
