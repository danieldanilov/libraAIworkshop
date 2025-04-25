import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Data setup
days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
categories = ["Checkout", "Shipping"]
data = np.array(
    [[12, 5, 18, 22, 30], [8, 4, 6, 5, 7]]  # Checkout Issues  # Shipping Issues
)

df = pd.DataFrame(data, index=categories, columns=days)

# Plotting
plt.figure(figsize=(8, 4))
sns.heatmap(df, annot=True, fmt="d", cmap="YlGnBu", cbar=False)

plt.title("Ticket Volume Heatmap (by Day & Category)")
plt.xlabel("Day of the Week")
plt.ylabel("Issue Category")
plt.tight_layout()
plt.savefig("heatmap_example.png")
plt.show()
