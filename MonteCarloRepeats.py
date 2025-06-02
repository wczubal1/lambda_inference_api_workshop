import numpy as np
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker # For formatting plot ticks

# Parameters
num_possible_items = 1024
sample_size = 100
num_monte_carlo_sims = 1000000

# To store results from each Monte Carlo simulation
results_repeat_profiles = [] # List of tuples: (n_pairs, n_triplets, n_quad_plus)

# Store other stats as before for the existing plots
results_num_uniques_in_sample = []
results_num_distinct_types_freq_2 = []
results_num_distinct_types_freq_3 = []
results_num_distinct_types_freq_4_plus = []
results_max_frequency_in_sample = []
results_total_distinct_types_seen = []

population = np.arange(num_possible_items)

print(f"Running {num_monte_carlo_sims} Monte Carlo simulations...")
for i_sim in range(num_monte_carlo_sims):
    if (i_sim + 1) % 1000 == 0:
        print(f"  Completed simulation {i_sim + 1}/{num_monte_carlo_sims}")

    current_sample = np.random.choice(population, size=sample_size, replace=True)
    frequency_counts = Counter(current_sample)
    
    uniques_count = 0
    pairs_count = 0       # Number of distinct item types that appeared twice
    triplets_count = 0    # Number of distinct item types that appeared three times
    quad_plus_count = 0 # Number of distinct item types that appeared four or more times
    max_freq = 0

    if frequency_counts: # Check if frequency_counts is not empty
        for count in frequency_counts.values(): # Iterate through the counts of each distinct item
            if count == 1:
                uniques_count += 1
            elif count == 2:
                pairs_count += 1
            elif count == 3:
                triplets_count += 1
            elif count >= 4:
                quad_plus_count += 1
            if count > max_freq:
                max_freq = count
    
    results_repeat_profiles.append((pairs_count, triplets_count, quad_plus_count))
    
    # Store other stats as before
    results_num_uniques_in_sample.append(uniques_count)
    results_num_distinct_types_freq_2.append(pairs_count) # Same as pairs_count
    results_num_distinct_types_freq_3.append(triplets_count) # Same as triplets_count
    results_num_distinct_types_freq_4_plus.append(quad_plus_count)
    results_max_frequency_in_sample.append(max_freq)
    results_total_distinct_types_seen.append(len(frequency_counts))

print("Monte Carlo simulations complete.")

# --- Analyze and Print Aggregated Results (includes previous analysis) ---
print("\n--- Aggregated Results from Monte Carlo Simulations ---")
series_freq_2 = pd.Series(results_num_distinct_types_freq_2)
print("\nDistribution of 'Number of Distinct Item Types Appearing Exactly Twice (Pairs)':")
print(series_freq_2.value_counts(normalize=True).sort_index())

count_analytical_match = 0
for i in range(num_monte_carlo_sims):
    if results_num_distinct_types_freq_2[i] == 1 and \
       results_num_distinct_types_freq_3[i] == 0 and \
       results_num_distinct_types_freq_4_plus[i] == 0 and \
       results_num_uniques_in_sample[i] == sample_size - 2:
        count_analytical_match += 1
prob_analytical_match_mc = count_analytical_match / num_monte_carlo_sims
print(f"MC Estimated P(Exactly one type appears twice AND 98 other types appear once): {prob_analytical_match_mc:.6f}")

series_freq_3 = pd.Series(results_num_distinct_types_freq_3)
print("\nDistribution of 'Number of Distinct Item Types Appearing Exactly Three Times (Triplets)':")
print(series_freq_3.value_counts(normalize=True).sort_index())

series_max_freq = pd.Series(results_max_frequency_in_sample)
print("\nDistribution of 'Maximum Frequency of any Single Item Type in a Sample':")
print(series_max_freq.value_counts(normalize=True).sort_index())

avg_distinct_types_seen = np.mean(results_total_distinct_types_seen)
print(f"\nAverage number of distinct item types seen per sample of {sample_size}: {avg_distinct_types_seen:.2f}")
theoretical_E_distinct = num_possible_items * (1 - (1 - 1/num_possible_items)**sample_size)
print(f"Theoretical E[distinct items seen]: {theoretical_E_distinct:.2f}")


# --- Analyze Repeat Profiles ---
print("\n--- Repeat Profile Analysis ---")
profile_counts = Counter(results_repeat_profiles)
print("Most common repeat profiles (pairs, triplets, 4+ repeats) and their counts:")
# Sort by count, then by profile tuple for consistent ordering if counts are same
sorted_profiles = sorted(profile_counts.items(), key=lambda item: (item[1], item[0]), reverse=True)

# Create a DataFrame for easier viewing and potential plotting of top N profiles
profile_df_data = []
for profile, count in sorted_profiles:
    profile_df_data.append({
        "Profile (Pairs, Triplets, 4+)": str(profile),
        "Count": count,
        "Proportion": count / num_monte_carlo_sims
    })
profile_summary_df = pd.DataFrame(profile_df_data)
print(profile_summary_df.head(15).to_string()) # Print top 15 profiles

# --- Plotting (Vertically Stacked for existing plots, new plot for profiles) ---
series_freq_2 = pd.Series(results_num_distinct_types_freq_2)
series_freq_3 = pd.Series(results_num_distinct_types_freq_3)
series_max_freq = pd.Series(results_max_frequency_in_sample)

num_existing_plots = 3
# Increased height slightly: num_existing_plots * 5 instead of 4.5
fig, axes = plt.subplots(nrows=num_existing_plots, ncols=1, figsize=(8, num_existing_plots * 5)) 

# Plot 1
series_freq_2.value_counts(normalize=True).sort_index().plot(kind='bar', ax=axes[0])
axes[0].set_title('Dist. of # Distinct Types with Freq=2 (Pairs)')
axes[0].set_xlabel("Number of Item Types with Frequency 2")
axes[0].set_ylabel("Proportion")
axes[0].tick_params(axis='x', rotation=0)
axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))
axes[0].grid(axis='y', linestyle='--', alpha=0.7)

# Plot 2
series_freq_3.value_counts(normalize=True).sort_index().plot(kind='bar', ax=axes[1])
axes[1].set_title('Dist. of # Distinct Types with Freq=3 (Triplets)')
axes[1].set_xlabel("Number of Item Types with Frequency 3")
axes[1].set_ylabel("Proportion")
axes[1].tick_params(axis='x', rotation=0)
axes[1].yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))
axes[1].grid(axis='y', linestyle='--', alpha=0.7)

# Plot 3
series_max_freq.value_counts(normalize=True).sort_index().plot(kind='bar', ax=axes[2])
axes[2].set_title('Dist. of Max Frequency in Sample')
axes[2].set_xlabel("Maximum Frequency of any Item Type")
axes[2].set_ylabel("Proportion")
axes[2].tick_params(axis='x', rotation=0)
axes[2].yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))
axes[2].grid(axis='y', linestyle='--', alpha=0.7)

plt.subplots_adjust(hspace=0.4) # Increased from default
plt.show()


# --- New Plot for Top N Repeat Profiles ---
# Plot the distribution of the most common repeat profiles
top_n_profiles = 15 # Number of top profiles to plot
profiles_to_plot = profile_summary_df.head(top_n_profiles)

plt.figure(figsize=(12, 7))
bars = plt.bar(profiles_to_plot["Profile (Pairs, Triplets, 4+)"], profiles_to_plot["Proportion"])
plt.xlabel("Repeat Profile (Pairs, Triplets, Items with Freq >= 4)")
plt.ylabel("Proportion of Simulations")
plt.title(f"Top {top_n_profiles} Most Common Repeat Profiles in {num_monte_carlo_sims} Simulations")
plt.xticks(rotation=45, ha="right") # Rotate labels for better readability
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.gca().yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))

# Add labels on top of bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.005, f'{yval*100:.1f}%', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()

print("\nNote on Repeat Profile Plot: Shows the proportion of simulations that resulted in "
      "a specific combination of (number of pairs, number of triplets, number of items with freq >= 4).")