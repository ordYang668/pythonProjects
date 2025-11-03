import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import MiniBatchKMeans
import os
import fnmatch
import time

def load_data(file_path):
    return pd.read_csv(file_path, delimiter='\t', header=None, names=['Process', 'File'])

def sample_data(data, sample_size):
    return data.sample(n=sample_size, random_state=42)

def vectorize_data(data):
    vectorizer = CountVectorizer(tokenizer=lambda x: x.split('/'), max_features=50)
    process_vec = vectorizer.fit_transform(data['Process']).toarray()
    file_vec = vectorizer.fit_transform(data['File']).toarray()
    return process_vec, file_vec

def cluster_data(process_vec, file_vec):
    combined_vec = np.hstack((process_vec, file_vec))
    mini_kmeans = MiniBatchKMeans(n_clusters=10, random_state=42)
    labels = mini_kmeans.fit_predict(combined_vec)
    return labels

def generate_detailed_rules(data, labels):
    rules = {}
    for cluster_id in set(labels):
        cluster_data = data.iloc[labels == cluster_id]
        if not cluster_data.empty:
            process_rules = set(cluster_data['Process'].apply(lambda x: os.path.dirname(x) + '/*'))
            file_rules = set(cluster_data['File'].apply(lambda x: os.path.dirname(x) + '/*'))
            rules[cluster_id] = (process_rules, file_rules)
    return rules

def remove_redundant_rules(rules):
    # Simplify rules by removing redundancies
    final_rules = []
    for process_rules, file_rules in rules.values():
        processed_file_rules = set()
        for file_rule in sorted(file_rules, key=lambda x: x.count('/'), reverse=True):
            if not any(fnmatch.fnmatch(file_rule, f_rule) for f_rule in processed_file_rules if f_rule != file_rule):
                processed_file_rules.add(file_rule)
        for process_rule in process_rules:
            final_rules.append((process_rule, processed_file_rules))
    return final_rules

def calculate_coverage(data, rules):
    matches = 0
    for _, row in data.iterrows():
        for process_rule, file_rules in rules:
            if fnmatch.fnmatch(row['Process'], process_rule) and any(fnmatch.fnmatch(row['File'], file_rule) for file_rule in file_rules):
                matches += 1
                break
    coverage = matches / len(data) * 100
    return coverage, matches

def performance_test(original_data_path, sample_size):
    start_time = time.time()  # Record start time

    # Load original data
    data = load_data(original_data_path)
    
    # Sample the data
    sampled_data = sample_data(data, sample_size)
    
    # Process sampled data
    process_vec, file_vec = vectorize_data(sampled_data)
    labels = cluster_data(process_vec, file_vec)
    rules = generate_detailed_rules(sampled_data, labels)
    refined_rules = remove_redundant_rules(rules)
    coverage, matches = calculate_coverage(sampled_data, refined_rules)

    end_time = time.time()  # Record end time
    processing_time = end_time - start_time

    # Save output to a text file
    output_path = f'performance_results_{sample_size}.txt'
    with open(output_path, 'w') as f:
        f.write("Generated Rules:\n")
        for process_rule, file_rules in refined_rules:
            for file_rule in file_rules:
                f.write(f"Process rule: {process_rule}, File rule: {file_rule}\n")
        f.write(f"\nCoverage: {coverage:.2f}%\n")
        f.write(f"Matches: {matches} of {len(sampled_data)}\n")
        f.write(f"Processing Time: {processing_time:.2f} seconds\n")

    print(f"Results for sample size {sample_size} have been saved to {output_path}")

def main():
    original_data_path = '/root/miniconda3/envs/pytorch/bisai/fileaccessdata.csv'  # Adjust the path as needed
    sample_sizes = [5000, 10000, 20000]

    for sample_size in sample_sizes:
        performance_test(original_data_path, sample_size)

if __name__ == "__main__":
    main()
