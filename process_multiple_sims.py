import pandas as pd
import os
from scipy.stats import multinomial # Added
from math import factorial # For multinomial coefficient if needed (though scipy handles it)
import itertools # To generate all possible sequences for ordering

def get_all_possible_sequences(length=10):
    """Generates all 2^length possible HT sequences of a given length."""
    if length == 0:
        return [""]
    shorter_sequences = get_all_possible_sequences(length - 1)
    result = []
    for s in shorter_sequences:
        result.append(s + "H")
        result.append(s + "T")
    return sorted(result) # Sort for a consistent ordering

ALL_10_FLIP_SEQUENCES = get_all_possible_sequences(10) # Should be 1024
NUM_POSSIBLE_SEQUENCES = len(ALL_10_FLIP_SEQUENCES)
PROB_SINGLE_SPECIFIC_SEQUENCE = (0.5)**10

def read_simulation_csv(filepath):
    # ... (same as before)
    try:
        df = pd.read_csv(filepath)
        if 'flip_sequence' not in df.columns or 'sequence_frequency' not in df.columns:
            print(f"Warning: File '{filepath}' is missing 'flip_sequence' or 'sequence_frequency' columns. Skipping.")
            return None
        # Ensure flip_sequence is string
        df['flip_sequence'] = df['flip_sequence'].astype(str)
        return df
    except FileNotFoundError: # ... (rest of error handling)
        print(f"Error: File not found at '{filepath}'. Skipping.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Warning: File '{filepath}' is empty. Skipping.")
        return None
    except Exception as e:
        print(f"An error occurred while reading CSV file '{filepath}': {e}. Skipping.")
        return None


def generate_frequency_summary_and_counts_vector(df, total_simulations):
    """
    Generates a summary of sequence frequencies and a counts vector for multinomial probability.

    Args:
        df (pandas.DataFrame): DataFrame with 'flip_sequence' and 'sequence_frequency'.
        total_simulations (int): Total number of simulations in this file.

    Returns:
        tuple: (list of duplicated sequences, count of single sequences, list of counts for all 1024 sequences)
    """
    if df is None or df.empty:
        return [], 0, [0] * NUM_POSSIBLE_SEQUENCES # Return zero vector if no data

    unique_sequences_df = df[['flip_sequence', 'sequence_frequency']].drop_duplicates().reset_index(drop=True)
    
    duplicated_df = unique_sequences_df[unique_sequences_df['sequence_frequency'] > 1].copy()
    duplicated_df.sort_values(by='sequence_frequency', ascending=False, inplace=True)
    
    duplicated_sequences_summary = []
    for _, row in duplicated_df.iterrows():
        duplicated_sequences_summary.append((row['flip_sequence'], row['sequence_frequency']))
        
    num_single_sequences = unique_sequences_df[unique_sequences_df['sequence_frequency'] == 1].shape[0]

    # --- Prepare counts vector for multinomial ---
    # This vector needs to have one entry for each of the 1024 possible sequences,
    # in a consistent order.
    
    # Get observed counts for sequences that actually appeared
    observed_counts_map = pd.Series(unique_sequences_df.sequence_frequency.values, 
                                    index=unique_sequences_df.flip_sequence).to_dict()

    multinomial_counts_vector = [0] * NUM_POSSIBLE_SEQUENCES
    for i, seq_key in enumerate(ALL_10_FLIP_SEQUENCES):
        multinomial_counts_vector[i] = observed_counts_map.get(seq_key, 0)
        
    # Sanity check: sum of counts should be total_simulations
    if sum(multinomial_counts_vector) != total_simulations:
        print(f"Warning: Sum of multinomial_counts_vector ({sum(multinomial_counts_vector)}) "
              f"does not match total_simulations ({total_simulations}). This can happen if "
              f"the input CSV was pre-filtered or doesn't represent all original trials.")
              # Or if the 'sequence_frequency' in the CSV was per unique sequence, not per original trial.
              # The current CSV 'sequence_frequency' *is* per unique sequence as requested.
              # The multinomial_counts_vector *needs* the count of each specific sequence from the 100 trials.
              # This means we need the *original* frequencies, not just the unique sequence frequencies.

    # REVISED APPROACH for multinomial_counts_vector based on your CSV structure:
    # The CSV has 'sequence_frequency' which is the count of that unique sequence.
    # The `multinomial_counts_vector` needs the count for each of the 1024 possible sequences.
    # The `generate_frequency_summary` correctly identified unique sequences and their counts.
    # This part is tricky because your CSV example shows 'sequence_frequency' as the total times *that unique sequence* appears.
    # e.g. TTHHTTHTTH,5 means TTHHTTHTTH appeared 5 times in the 100 trials.
    # This is exactly what `multinomial_counts_vector` needs for that sequence's slot.

    return duplicated_sequences_summary, num_single_sequences, multinomial_counts_vector


def calculate_multinomial_prob_of_distribution(counts_vector, total_trials):
    """
    Calculates the probability of observing a specific distribution of counts
    for all 1024 possible sequences.

    Args:
        counts_vector (list): A list of 1024 elements, where each element is the
                              observed frequency of the corresponding unique sequence.
        total_trials (int): The total number of simulations (e.g., 100).

    Returns:
        float: The multinomial probability.
    """
    if sum(counts_vector) != total_trials:
        print(f"Error in multinomial calculation: Sum of counts ({sum(counts_vector)}) "
              f"does not equal total trials ({total_trials}). Probability will be 0 or incorrect.")
        # scipy.stats.multinomial.pmf will likely return 0 if sum(counts) != n
    
    # Probabilities for each of the 1024 categories (each specific sequence)
    # Each specific sequence has a probability PROB_SINGLE_SPECIFIC_SEQUENCE of occurring.
    p_categories = [PROB_SINGLE_SPECIFIC_SEQUENCE] * NUM_POSSIBLE_SEQUENCES
    
    # Ensure probabilities sum to 1 (they do because 1024 * (1/1024) = 1)
    # print(f"Sum of p_categories for multinomial: {sum(p_categories)}")

    try:
        prob = multinomial.pmf(x=counts_vector, n=total_trials, p=p_categories)
        return prob
    except ValueError as e:
        print(f"ValueError during multinomial.pmf: {e}")
        print(f"  Counts vector sum: {sum(counts_vector)}, n: {total_trials}")
        print(f"  Length of counts vector: {len(counts_vector)}, Length of p_categories: {len(p_categories)}")
        # print(f"  Counts vector (first 10): {counts_vector[:10]}")
        # print(f"  p_categories (first 10): {p_categories[:10]}")
        return 0.0 # Or handle error as appropriate

def main():
    # Define results directory
    results_dir = "results"
    
    # Ensure the results directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Input files are now in the results directory
    file_paths = [
        os.path.join(results_dir, "detailed_analyzed_coin_flipsDeepSeekV3NoSeed.csv"),
        os.path.join(results_dir, "detailed_analyzed_coin_flipsDSV3Temp1_5.csv"),
        os.path.join(results_dir, "detailed_analyzed_coin_flipsDSR1Temp1Embedded.csv"),
        os.path.join(results_dir, "detailed_analyzed_coin_flipsDSR1Temp1Final.csv"),
        os.path.join(results_dir, "detailed_analyzed_coin_flipsDSR1Temp1_5Embedded.csv"),
        os.path.join(results_dir, "detailed_analyzed_coin_flipsDSR1Temp1_5Final.csv")
    ]
    
    # Output file is also in the results directory
    output_summary_file = os.path.join(results_dir, "all_files_frequency_and_multinomial_summary.txt")

    # Pre-generate all 1024 possible sequences once if not already global
    # (It's global: ALL_10_FLIP_SEQUENCES)
    print(f"Total possible unique 10-flip sequences: {NUM_POSSIBLE_SEQUENCES}")
    print(f"Probability of any single specific sequence: {PROB_SINGLE_SPECIFIC_SEQUENCE}")


    with open(output_summary_file, 'w', encoding='utf-8') as outfile:
        for filepath in file_paths:
            print(f"\nProcessing file: {filepath}...")
            outfile.write(f"--- Summary for: {os.path.basename(filepath)} ---\n")
            
            detailed_df = read_simulation_csv(filepath)
            
            if detailed_df is not None and not detailed_df.empty:
                # Determine total simulations from the sum of 'sequence_frequency' of unique sequences
                # This assumes 'sequence_frequency' in the CSV is the count of that unique sequence from 100 trials.
                # Correct way to get total_simulations for a file if not explicitly known:
                # It should be the number of rows in the *original* simulation log, or sum of frequencies.
                # For the multinomial, 'n' (total_trials) must be the sum of the counts vector.
                
                # Let's assume the number of rows in the detailed_df *is* the number of original trials (e.g., 100)
                # This is crucial. If detailed_df is already summarized, this assumption is wrong.
                # Based on your CSV example, it looks like each row is one of the 100 original simulations.
                total_simulations_in_file = len(detailed_df) # Number of rows in the CSV
                
                outfile.write(f"Total simulations in this file: {total_simulations_in_file}\n")
                outfile.write("Flip Sequence, Frequency\n")

                # `sequence_frequency` in the CSV is already the count of how many times *that specific sequence* appeared.
                # We need to map these observed sequences and their counts to the full 1024-slot vector.
                
                # Create a map of observed sequence -> its count from the 'sequence_frequency' column
                # considering only unique (sequence, frequency) pairs for this map.
                unique_sequence_counts_map = detailed_df[['flip_sequence', 'sequence_frequency']].drop_duplicates().set_index('flip_sequence')['sequence_frequency'].to_dict()

                multinomial_counts_vector = [0] * NUM_POSSIBLE_SEQUENCES
                for i, seq_key in enumerate(ALL_10_FLIP_SEQUENCES):
                    multinomial_counts_vector[i] = unique_sequence_counts_map.get(seq_key, 0)
                
                # Verify sum of multinomial_counts_vector equals total_simulations_in_file
                if sum(multinomial_counts_vector) != total_simulations_in_file:
                    print(f"CRITICAL WARNING for {os.path.basename(filepath)}: Sum of constructed multinomial counts ({sum(multinomial_counts_vector)}) "
                          f"does not match total simulations in file ({total_simulations_in_file}). "
                          "This indicates an issue with interpreting 'sequence_frequency' or the CSV structure. "
                          "The multinomial probability will be incorrect.")
                    outfile.write(f"Error: Could not verify consistency for multinomial calculation. Sum of counts: {sum(multinomial_counts_vector)}, Expected total: {total_simulations_in_file}\n")

                
                # Regenerate duplicated_summary and single_count for the text report based on unique_sequence_counts_map
                duplicated_summary_report = []
                single_count_report = 0
                sorted_unique_counts = sorted(unique_sequence_counts_map.items(), key=lambda item: item[1], reverse=True)

                for seq, freq in sorted_unique_counts:
                    if freq > 1:
                        duplicated_summary_report.append((seq, freq))
                    elif freq == 1:
                        single_count_report += 1
                
                if duplicated_summary_report:
                    for seq, freq in duplicated_summary_report:
                        outfile.write(f"{seq},{freq}\n")
                else:
                    outfile.write("No sequences appeared more than once.\n")
                
                outfile.write("--------------------------\n")
                outfile.write(f"Single Occurrences (Unique Sequences),{single_count_report}\n")

                # Calculate multinomial probability if counts sum correctly
                if sum(multinomial_counts_vector) == total_simulations_in_file and total_simulations_in_file > 0 :
                    prob_dist = calculate_multinomial_prob_of_distribution(multinomial_counts_vector, total_simulations_in_file)
                    outfile.write(f"Multinomial Probability of this specific distribution of sequence frequencies: {prob_dist:.4e}\n") # scientific notation
                elif total_simulations_in_file == 0:
                     outfile.write(f"Multinomial Probability: N/A (no simulations)\n")
                else: # Sum mismatch
                     outfile.write(f"Multinomial Probability: Not calculated due to count mismatch.\n")

            else:
                outfile.write("Could not process this file or file was empty/invalid.\n")
            
            outfile.write("\n\n")

    print(f"\nSummary report generated: {output_summary_file}")

if __name__ == "__main__":
    main()