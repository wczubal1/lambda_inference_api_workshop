##extract_flips_embedded_only_regex provides the "Priority 3 only" extraction. Its results go into coin_flips_embedded_only_{timestamp}.txt.
##extract_flips_prioritized_logic provides the "Priority 1 then 2 then 3 (and a final fallback)" extraction. Its results go into coin_flips_prioritized_{timestamp}.txt.
##Now, when you run this script, you'll get three output files. You can then compare the contents of coin_flips_prioritized_...txt and coin_flips_embedded_only_...txt to see how often the extraction methods differ and which one is more consistently getting the sequence you intend to capture from the LLM's output. The raw output file will be very helpful if you need to debug why an extraction failed or to refine the extraction logic further.

import os
from dotenv import load_dotenv
import autogen
from datetime import datetime
import time
import re # Import regex module

# --- Environment and Config (same as your original) ---
# os.environ["OPENAI_API_REQUEST_TIMEOUT"] = "120"
os.environ["AUTOGEN_USE_DOCKER"] = "False"
load_dotenv()

LAMBDA_API_KEY = os.getenv("LAMBDA_INFERENCE_API_KEY")
LAMBDA_BASE_URL = os.getenv("LAMBDA_INFERENCE_API_BASE")

if not LAMBDA_API_KEY:
    raise ValueError("LAMBDA_INFERENCE_API_KEY environment variable not set or empty.")
if not LAMBDA_BASE_URL:
    raise ValueError("LAMBDA_INFERENCE_API_BASE environment variable not set or empty.")

config_list = [{
    "model": "deepseek-r1",
    "api_key": LAMBDA_API_KEY,
    "base_url": LAMBDA_BASE_URL,
    "api_type": "openai",
}]

llm_config = {
    "config_list": config_list,
    "temperature": 1.5, # Original temperature
    "max_tokens": 1000,
}

COIN_SIMULATOR_SYSTEM_MESSAGE = ( # Using your latest aggressive prompt
    "You are a direct output coin flip simulator. Your ONLY job is to output a 10-character random and unbiased coin flip sequence ('H'/'T'), "
    "a one-sentence explanation, and the word TERMINATE. NO OTHER TEXT, NO THINKING, NO PREAMBLE. "
    "Your response MUST be ONLY the formatted output.\n\n"
    "STRICT FORMAT (NO DEVIATIONS):\n"
    "[10_CHAR_SEQUENCE_HT_ONLY_NO_SPACES_OR_OTHER_CHARS]\n"
    "---Explanation---\n"
    "[ONE_SENTENCE_EXPLANATION_OF_RANDOMIZATION_METHOD]\n"
    "TERMINATE\n\n"
    "EXAMPLE OF YOUR EXACT AND ONLY OUTPUT:\n"
    "THTHTHTHHT\n"
    "---Explanation---\n"
    "Each flip was simulated with a 50% chance for H or T, independently.\n"
    "TERMINATE\n\n"
    "Produce the final answer in the specified format."
)
# --- End Environment and Config ---

# --- NEW EXTRACTION FUNCTIONS ---
def extract_flips_embedded_only_regex(full_response_content):
    """
    Priority 3 ONLY: Extracts the *first* 10-character H/T sequence found anywhere
    within any line using regex. Returns empty string if none found.
    """
    if not isinstance(full_response_content, str):
        return ""
    
    ht_pattern = re.compile(r"([HT]{10})")
    lines = full_response_content.splitlines()
    for line in lines:
        # No strip here, regex will find it even with leading/trailing spaces in the line content
        match = ht_pattern.search(line) 
        if match:
            return match.group(1) # Return the first one found in any line
    return "" # If no embedded sequence found in any line

def extract_flips_prioritized_logic(full_response_content):
    """
    Prioritized Logic:
    1. Line is ONLY 10 H/T characters.
    2. Line STARTS WITH 10 H/T characters.
    3. Fallback: Regex for embedded 10 H/T sequence in any line.
    4. Super Fallback: Concatenate all H/T and take first 10.
    """
    if not isinstance(full_response_content, str):
        return ""

    lines = full_response_content.splitlines()
    ht_pattern_embedded = re.compile(r"([HT]{10})")

    # Priority 1 & 2 (Clean lines)
    for line in lines:
        cleaned_line = line.strip()
        # Priority 1: Line is ONLY 10 H/T characters
        if len(cleaned_line) == 10 and all(c in 'HT' for c in cleaned_line):
            return cleaned_line
        # Priority 2: Line STARTS WITH 10 H/T characters
        if len(cleaned_line) >= 10 and all(c in 'HT' for c in cleaned_line[:10]):
            return cleaned_line[:10]

    # Priority 3: Regex for embedded sequence (if not found by P1/P2)
    for line in lines:
        # Search in the original line (strip not strictly necessary for regex but okay)
        match = ht_pattern_embedded.search(line.strip()) 
        if match:
            return match.group(1)
            
    # Priority 4 (Super Fallback): extract first 10 H/T characters found anywhere in the entire content
    found_chars = "".join(c for c in full_response_content if c in "HT")
    if len(found_chars) >= 10:
        return found_chars[:10]
    
    return "" # Return empty if nothing suitable is found

# --- End NEW EXTRACTION FUNCTIONS ---


def run_coin_flip_simulation():
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        system_message="You are a coordinator.",
        human_input_mode="NEVER",
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
    )

    # Store raw responses and results from different extraction methods
    all_raw_responses = [] # Stores the full LLM response (after TERMINATE removal)
    results_prioritized_extraction = [] # For extract_flips_prioritized_logic
    results_embedded_only_extraction = [] # For extract_flips_embedded_only_regex

    print("Attempting to initialize AssistantAgent...")
    try:
        coin_flipper = autogen.AssistantAgent(
            name="coin_flipper",
            llm_config=llm_config,
            system_message=COIN_SIMULATOR_SYSTEM_MESSAGE
        )
        print("AssistantAgent initialized successfully.")
    except Exception as e:
        print(f"ERROR initializing AssistantAgent: {e}")
        import traceback
        traceback.print_exc()
        return

    num_simulations = 100 # As requested
    for i in range(num_simulations):
        print(f"\n--- Starting Simulation {i+1}/{num_simulations} ---")
        chat_message = f"Simulate 10 flips for simulation {i+1}. Output ONLY in the specified format and end with TERMINATE."
        
        raw_llm_output_cleaned = "Error: Chat did not produce a usable response."

        try:
            # print(f"Attempting to initiate chat for simulation {i+1}...") # Less verbose
            chat_res = user_proxy.initiate_chat(
                coin_flipper,
                message=chat_message,
                max_rounds=2 
            )
            # print(f"Chat for simulation {i+1} completed (or reached max_rounds).") # Less verbose

            flipper_final_reply_content = ""
            if chat_res and chat_res.chat_history:
                for msg_item in reversed(chat_res.chat_history):
                    if msg_item.get("name") == coin_flipper.name and msg_item.get("content"):
                        flipper_final_reply_content = str(msg_item.get("content")).strip()
                        if flipper_final_reply_content.rstrip().endswith("TERMINATE"):
                            terminate_index = flipper_final_reply_content.rfind("TERMINATE")
                            if terminate_index != -1:
                                flipper_final_reply_content = flipper_final_reply_content[:terminate_index].strip()
                        break 
            
            if flipper_final_reply_content:
                raw_llm_output_cleaned = flipper_final_reply_content
            elif chat_res and chat_res.summary:
                print(f"Warning (Sim {i+1}): No direct message from {coin_flipper.name} containing TERMINATE found, using chat summary.")
                raw_llm_output_cleaned = chat_res.summary
            else:
                print(f"Error (Sim {i+1}): No valid response or summary from Coin Flipper.")
        
        except Exception as e:
            print(f"CRITICAL ERROR during chat for simulation {i+1}: {e}")
            # import traceback # Only if very verbose debugging is needed
            # traceback.print_exc()
            raw_llm_output_cleaned = f"Error: Exception during chat - {e}"

        all_raw_responses.append(raw_llm_output_cleaned) # Save the processed LLM output

        # Perform both extractions
        flips_prioritized = extract_flips_prioritized_logic(raw_llm_output_cleaned)
        flips_embedded_only = extract_flips_embedded_only_regex(raw_llm_output_cleaned)

        results_prioritized_extraction.append(flips_prioritized)
        results_embedded_only_extraction.append(flips_embedded_only)
        
        print(f"Sim {i+1}: Prioritized Extr: '{flips_prioritized}', Embedded-Only Extr: '{flips_embedded_only}'")
        
        user_proxy.reset()
        coin_flipper.reset()
        time.sleep(0.5) # Small delay to avoid overwhelming API if it's remote & sensitive

    # --- Save results to separate files ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # File for Prioritized Extraction Results
    filename_prioritized = f"coin_flips_prioritized_{timestamp}.txt"
    with open(filename_prioritized, "w", encoding="utf-8") as f_prioritized:
        f_prioritized.write(f"Coin Flip Simulation Results (Prioritized Extraction)\n")
        f_prioritized.write(f"Timestamp: {timestamp}\n")
        f_prioritized.write(f"Total Simulations Attempted: {num_simulations}\n")
        f_prioritized.write("==================================================\n\n")
        f_prioritized.write("Validated 10-flip sequences (Prioritized Logic):\n")
        valid_count_prioritized = 0
        for idx, seq in enumerate(results_prioritized_extraction):
            if len(seq) == 10 and all(c in 'HT' for c in seq):
                f_prioritized.write(f"Simulation {idx+1} sequence: {seq}\n")
                valid_count_prioritized +=1
            else:
                f_prioritized.write(f"Simulation {idx+1} sequence: INVALID_OR_EMPTY ('{seq}')\n") # Log invalid ones too
        print(f"\nResults (Prioritized Extraction) saved to {filename_prioritized} ({valid_count_prioritized} valid sequences)")

    # File for Embedded-Only (Regex) Extraction Results
    filename_embedded = f"coin_flips_embedded_only_{timestamp}.txt"
    with open(filename_embedded, "w", encoding="utf-8") as f_embedded:
        f_embedded.write(f"Coin Flip Simulation Results (Embedded-Only Regex Extraction)\n")
        f_embedded.write(f"Timestamp: {timestamp}\n")
        f_embedded.write(f"Total Simulations Attempted: {num_simulations}\n")
        f_embedded.write("=========================================================\n\n")
        f_embedded.write("Validated 10-flip sequences (Embedded-Only Regex Logic):\n")
        valid_count_embedded = 0
        for idx, seq in enumerate(results_embedded_only_extraction):
            if len(seq) == 10 and all(c in 'HT' for c in seq):
                f_embedded.write(f"Simulation {idx+1} sequence: {seq}\n")
                valid_count_embedded += 1
            else:
                f_embedded.write(f"Simulation {idx+1} sequence: INVALID_OR_EMPTY ('{seq}')\n")
        print(f"Results (Embedded-Only Extraction) saved to {filename_embedded} ({valid_count_embedded} valid sequences)")

    # Optionally, save the raw LLM responses too
    filename_raw = f"coin_flips_raw_llm_outputs_{timestamp}.txt"
    with open(filename_raw, "w", encoding="utf-8") as f_raw:
        f_raw.write(f"Raw LLM Outputs (after TERMINATE removal)\n")
        f_raw.write(f"Timestamp: {timestamp}\n")
        f_raw.write(f"Total Simulations: {num_simulations}\n")
        f_raw.write("=========================================\n\n")
        for idx, raw_output in enumerate(all_raw_responses):
            f_raw.write(f"--- Simulation {idx+1} Raw Output ---\n{raw_output}\n-----------------------------------\n\n")
    print(f"Raw LLM outputs saved to {filename_raw}")


if __name__ == "__main__":
    run_coin_flip_simulation()