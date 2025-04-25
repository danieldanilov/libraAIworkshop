import matplotlib.pyplot as plt

# Data
categories = ["Checkout Issues", "Shipping Issues"]
totals = [330, 100]  # Simulated totals over a period

# Plotting
plt.figure(figsize=(6, 4))
plt.bar(categories, totals)

plt.title("Total Tickets by Category")
plt.ylabel("Total Number of Tickets")
plt.tight_layout()
plt.savefig("bar_graph_example.png")
plt.show()
