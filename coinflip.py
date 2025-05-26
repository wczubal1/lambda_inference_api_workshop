import os
from dotenv import load_dotenv
import autogen
from datetime import datetime
import time

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
    # "price": [0.0, 0.0]
}]

llm_config = {
    "config_list": config_list,
    "seed": 42,
    "temperature": 0.2, # Lowered temperature
    "max_tokens": 400,
}

COIN_SIMULATOR_SYSTEM_MESSAGE = (
    "You are a direct output coin flip simulator. Your ONLY job is to IMMEDIATELY output a 10-character coin flip sequence ('H'/'T'), "
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
    "If your output contains any text before the 10-character sequence or any 'thinking' text, it is incorrect. "
    "Produce ONLY the final answer in the specified format."
)

def validate_flips(flip_result_str): # Parameter renamed for clarity
    if not isinstance(flip_result_str, str):
        return False
    if len(flip_result_str) < 10: # Check if we even have 10 chars for sequence
        return False
    sequence_part = flip_result_str[:10] # Assuming sequence is at the start
    return all(c in 'HT' for c in sequence_part)

def extract_flips(full_response_content):
    if not isinstance(full_response_content, str):
        return ""
    lines = full_response_content.splitlines()
    for line in lines:
        cleaned_line = line.strip()
        if len(cleaned_line) >= 10 and all(c in 'HT' for c in cleaned_line[:10]):
            return cleaned_line[:10]
        if len(cleaned_line) == 10 and all(c in 'HT' for c in cleaned_line): # Handles case where line is *only* the sequence
            return cleaned_line
    # Fallback: extract first 10 H/T characters found anywhere
    found_chars = "".join(c for c in full_response_content if c in "HT")
    return found_chars[:10]

def run_coin_flip_simulation():
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        system_message="You are a coordinator.",
        human_input_mode="NEVER",
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
    )

    results = []
    full_responses = []

    def save_results_manual(full_message, processed_flips_str):
        full_responses.append(full_message)
        # Validate the processed_flips_str which should be the 10-char sequence
        if len(processed_flips_str) == 10 and all(c in 'HT' for c in processed_flips_str):
            results.append(processed_flips_str)
            print(f"Valid flip recorded: {processed_flips_str}")
        else:
            # This case should be less common now if extract_flips is good
            print(f"Invalid flip string passed to save_results_manual: '{processed_flips_str}' from full message: '{full_message[:100]}...'")

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

    for i in range(100): # Number of simulations
        print(f"\n--- Starting Simulation {i+1} ---")
        chat_message = f"Simulate 10 flips for simulation {i+1}. Output ONLY in the specified format and end with TERMINATE."
        
        # Default response content in case of issues
        last_response_content_for_processing = "Error: Chat did not produce a usable response."

        try:
            print(f"Attempting to initiate chat for simulation {i+1}...")
            chat_res = user_proxy.initiate_chat(
                coin_flipper,
                message=chat_message,
                max_rounds=2 # Kept at 2, as it seems to take 2 assistant turns
            )
            print(f"Chat for simulation {i+1} completed (or reached max_rounds).")

            flipper_final_reply_content = ""
            if chat_res and chat_res.chat_history:
                for msg_item in reversed(chat_res.chat_history): # Use msg_item
                    if msg_item.get("name") == coin_flipper.name and msg_item.get("content"): # Use msg_item
                        flipper_final_reply_content = str(msg_item.get("content")).strip()
                        if flipper_final_reply_content.rstrip().endswith("TERMINATE"):
                            terminate_index = flipper_final_reply_content.rfind("TERMINATE")
                            if terminate_index != -1:
                                flipper_final_reply_content = flipper_final_reply_content[:terminate_index].strip()
                        break 
            
            if flipper_final_reply_content:
                last_response_content_for_processing = flipper_final_reply_content
            elif chat_res and chat_res.summary:
                print(f"Warning: No direct message from {coin_flipper.name} containing TERMINATE found, using chat summary.")
                last_response_content_for_processing = chat_res.summary # This might not be ideal
            else:
                print(f"Error: Simulation {i+1} - No valid response or summary from Coin Flipper.")
                # last_response_content_for_processing remains the default error message

        except Exception as e:
            print(f"CRITICAL ERROR during chat for simulation {i+1}: {e}")
            import traceback
            traceback.print_exc()
            last_response_content_for_processing = f"Error: Exception during chat - {e}"

        print(f"Simulation {i+1} raw full response (after TERMINATE removal):\nSTART>>>\n{last_response_content_for_processing}\n<<<END")
        
        processed_flips_str = extract_flips(last_response_content_for_processing)
            
        print(f"Simulation {i+1} processed result: {processed_flips_str}")
        save_results_manual(last_response_content_for_processing, processed_flips_str)
        
        user_proxy.reset()
        coin_flipper.reset()

    # Save full messages and statistics to file
    if full_responses:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"coin_flip_results_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("Coin Flip Simulation Results\n")
            f.write("==========================\n\n")
            for idx, full_msg in enumerate(full_responses, 1):
                f.write(f"--- Simulation {idx} Raw Full Response (after TERMINATE removal) ---\n{full_msg}\n---------------------------------------\n\n")
            
            f.write("\nValidated 10-flip sequences:\n")
            valid_flip_strings = [r for r in results if isinstance(r, str) and len(r) == 10 and all(c in 'HT' for c in r)]
            for idx, result_str in enumerate(valid_flip_strings, 1):
                f.write(f"Simulation {idx} sequence: {result_str}\n")
            
            total_heads = sum(result_str.count('H') for result_str in valid_flip_strings)
            total_flips = len(valid_flip_strings) * 10
            heads_percentage = (total_heads / total_flips) * 100 if total_flips > 0 else 0
            
            f.write(f"\nStatistics:\n")
            f.write(f"Total validated simulations: {len(valid_flip_strings)}\n")
            f.write(f"Total flips (from validated results): {total_flips}\n")
            f.write(f"Total heads: {total_heads}\n")
            f.write(f"Heads percentage: {heads_percentage:.2f}%\n")
        
        print(f"\nResults saved to {filename}")
    else:
        print("\nNo simulation responses to save.")

if __name__ == "__main__":
    run_coin_flip_simulation()