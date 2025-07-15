import matplotlib.pyplot as plt
import numpy as np

def plot_fraction_histogram(bin_lowers, bin_uppers, fractions, xlabel="Diameter, μm", ylabel="Fraction, %", title="Fraction Histogram"):
    """
    Plots a histogram for fractions on a specific grid with lower and upper boundaries.
    """
    bin_widths = np.array(bin_uppers) - np.array(bin_lowers)
    bin_centers = np.array(bin_lowers) + bin_widths / 2

    plt.figure(figsize=(8, 5))
    plt.bar(bin_centers, fractions, width=bin_widths, align='center', edgecolor='black', alpha=0.7)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xscale('log')
    plt.ylim(0, 50)
    plt.xlim(1e-2, 2000)  # Set x-axis limits
    plt.grid(True, which="both", ls="--",alpha=0.5)
    plt.tight_layout()
    plt.show()
