import argparse
import os
import multiprocessing
import pickle

from classes.GoogleVerification import GoogleVerifierSerpAPI
from classes.QueryGeneration import VllmQueryGeneration
from datasets import load_dataset
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="2,3"
# 2. Specify the model name from the Hugging Face Hub

def main(args):

    #Import distribution of seed topics
    # could be previous google searches
    # a random topic 
    # or sentence on a fact
    ds = load_dataset("google-research-datasets/natural_questions", "default")
    topics = ds["question"].text[:100]

    #Generate candidate examples
    gen = VllmQueryGeneration(model_name=args.model_name)
    tmp_path = f'{args.tmp_dir}/candidates.pkl'
    # prevent vllm from not dying
    p = multiprocessing.Process(target=gen.generate, args=(topics,tmp_path,))
    p.start()
    p.join()

    # open list of candidates
    with open(tmp_path, "rb") as f:
        q_candidates = pickle.load(f)

    
    # Brute force search the query candidates and mark the properties
    verifier = GoogleVerifierSerpAPI()
    verified_queries_df = verifier.verify(q_candidates) #pandas df
    
    # Save to excel sheet
    excel_path = os.path.join(args.output_dir, "verified_queries.xlsx")
    verified_queries_df.to_excel(excel_path, index=False)
    print(f"Saved verified queries to: {excel_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate queries from topics and verify them using GoogleVerifierSerpAPI."
    )

    parser.add_argument(
        "--dtype",
        type=str,
        default="data",
        help="Type of data either a file or huggingface"
    )

    parser.add_argument(
        "--input_dir",
        type=str,
        default="data",
        help="Path to the input data directory (if needed)."
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default="results",
        help="Path to the output directory where results will be saved."
    )

    parser.add_argument(
        "--tmp_dir",
        type=str,
        default="data",
        help="Path to the input data directory (if needed)."
    )

    parser.add_argument(
        "--model_name",
        type=str,
        default="meta-llama/Llama-3.1-70B-Instruct",
        help="Path to the input data directory (if needed)."
    )
    
    args = parser.parse_args()
    
    main(args.input_dir, args.output_dir)