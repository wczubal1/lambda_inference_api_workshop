import re
import pandas as pd
from scipy.stats import binom
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

# --- parse_simulation_results_file function (remains the same) ---
def parse_simulation_results_file(filepath):
    sequences = []
    pattern = re.compile(r"Simulation \d+ sequence: ([HT]{10})")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    sequence = match.group(1)
                    if len(sequence) == 10 and all(c in 'HT' for c in sequence):
                        sequences.append(sequence)
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
        return []
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return []
    if not sequences:
        print(f"No valid 'Simulation X sequence: [HT]{{10}}' lines found in {filepath}.")
    return sequences


def analyze_coin_flips_to_df(flip_sequences):
    """
    Analyzes a list of coin flip sequences to create a detailed DataFrame with statistics,
    including the frequency of each unique sequence.
    """
    if not flip_sequences:
        print("No flip sequences to analyze.")
        return None

    data_for_df = []
    n_trials = 10
    p_success = 0.5

    for i, seq in enumerate(flip_sequences):
        if len(seq) == n_trials and all(c in 'HT' for c in seq):
            num_heads = seq.count('H')
            num_tails = n_trials - num_heads
            binomial_prob_for_this_num_heads = binom.pmf(num_heads, n_trials, p_success)
            
            data_for_df.append({
                "simulation_id": i + 1,
                "flip_sequence": seq,
                "num_heads": num_heads,
                "num_tails": num_tails,
                "binomial_probability_of_heads": binomial_prob_for_this_num_heads
                # 'sequence_frequency' will be added later
            })
        else:
            print(f"Warning: Skipping invalid sequence: '{seq}' (ID {i+1} in input list)")
    
    if not data_for_df:
        print("No valid sequences processed to create initial detailed DataFrame.")
        return None
            
    df = pd.DataFrame(data_for_df)

    # Add the 'sequence_frequency' column
    # This counts how many times each 'flip_sequence' appears in the DataFrame
    if not df.empty and 'flip_sequence' in df.columns:
        df['sequence_frequency'] = df.groupby('flip_sequence')['flip_sequence'].transform('size')
        # Alternative using value_counts and map:
        # sequence_counts = df['flip_sequence'].value_counts()
        # df['sequence_frequency'] = df['flip_sequence'].map(sequence_counts)
    else:
        # Handle case where df might be empty or column missing, though unlikely with prior checks
        df['sequence_frequency'] = 0


    return df

# --- create_summary_for_plotting function (remains the same) ---
def create_summary_for_plotting(detailed_df, total_simulations):
    if detailed_df is None or detailed_df.empty: return None
    n_trials = 10
    p_success = 0.5
    observed_head_counts = detailed_df['num_heads'].value_counts().sort_index()
    summary_data = []
    for k_heads in range(n_trials + 1):
        binomial_prob = binom.pmf(k_heads, n_trials, p_success)
        observed_freq = observed_head_counts.get(k_heads, 0)
        observed_prob = observed_freq / total_simulations if total_simulations > 0 else 0
        summary_data.append({
            "num_heads": k_heads,
            "binomial_probability": binomial_prob,
            "observed_frequency": observed_freq,
            "observed_probability": observed_prob
        })
    return pd.DataFrame(summary_data)

# --- plot_single_yaxis_percentages function (remains the same) ---
def plot_single_yaxis_percentages(summary_df):
    if summary_df is None or summary_df.empty:
        print("Summary DataFrame is empty, cannot plot.")
        return
    num_heads = summary_df["num_heads"]
    binomial_probs = summary_df["binomial_probability"]
    observed_probs = summary_df["observed_probability"]
    x = np.arange(len(num_heads))
    width = 0.35
    fig, ax = plt.subplots(figsize=(14, 8))
    def prob_to_percent_str(val):
        return f"{val*100:.1f}%"
    rects1 = ax.bar(x - width/2, binomial_probs, width, label='Binomial Probability (Theoretical)', color='skyblue')
    ax.bar_label(rects1, padding=3, labels=[prob_to_percent_str(p) for p in binomial_probs])
    rects2 = ax.bar(x + width/2, observed_probs, width, label='Observed Probability (from Simulations)', color='lightcoral')
    ax.bar_label(rects2, padding=3, labels=[prob_to_percent_str(p) for p in observed_probs])
    ax.set_ylabel('Probability / Observed Proportion')
    ax.set_xlabel('Number of Heads in 10 Flips')
    ax.set_title('Comparison of Theoretical Binomial Probability and Observed Simulation Proportion')
    ax.set_xticks(x)
    ax.set_xticklabels(num_heads)
    ax.legend()
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    fig.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


def main():
    """
    Main function to orchestrate reading, parsing, analyzing, and plotting.
    """
    file_to_analyze = "C:/Users/witol/Tech/LLM/Hackathon2/lambda_inference_api_workshop/coin_flip_results_20250525_002402.txt" 
    
    if not os.path.exists(file_to_analyze):
        print(f"The file '{file_to_analyze}' does not exist. Please check the path.")
        return

    print(f"Reading simulations from: {file_to_analyze}")
    sequences = parse_simulation_results_file(file_to_analyze)
    
    if sequences:
        total_simulations = len(sequences)
        print(f"Successfully parsed {total_simulations} simulation sequences.")
            
        detailed_results_df = analyze_coin_flips_to_df(sequences) # This now includes 'sequence_frequency'
        
        if detailed_results_df is not None and not detailed_results_df.empty:
            print("\nDetailed Analysis DataFrame (Head):")
            print(detailed_results_df.head().to_string()) # Print more of the head to see the new column
            
            # You can also print specific rows to check the sequence_frequency
            # For example, if you know a sequence that might be duplicated:
            # print("\nChecking a potentially duplicated sequence:")
            # print(detailed_results_df[detailed_results_df['flip_sequence'] == 'HTHTHTHTHT'])


            output_detailed_csv = "detailed_analyzed_coin_flips.csv"
            try:
                detailed_results_df.to_csv(output_detailed_csv, index=False)
                print(f"\nDetailed analysis saved to {output_detailed_csv}")
            except Exception as e:
                print(f"Error saving detailed DataFrame to CSV: {e}")

            summary_for_plot_df = create_summary_for_plotting(detailed_results_df, total_simulations)
            if summary_for_plot_df is not None:
                print("\nSummary DataFrame for Plotting:")
                print(summary_for_plot_df.to_string())
                
                plot_single_yaxis_percentages(summary_for_plot_df) 
            else:
                print("Could not generate summary DataFrame for plotting.")
        else:
            print("Could not generate detailed analysis DataFrame.")
    else:
        print("No sequences were parsed from the file.")

if __name__ == "__main__":
    main()