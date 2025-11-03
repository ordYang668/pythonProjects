import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import MiniBatchKMeans
import os
import fnmatch

# 载入数据
def load_data(file_path):
    return pd.read_csv(file_path, delimiter='\t', header=None, names=['Process', 'File'])

# 数据向量化
def vectorize_data(data):
    process_vectorizer = CountVectorizer(tokenizer=lambda x: x.split('/'), max_features=50)
    file_vectorizer = CountVectorizer(tokenizer=lambda x: x.split('/'), max_features=50)

    process_vec = process_vectorizer.fit_transform(data['Process']).toarray()
    file_vec = file_vectorizer.fit_transform(data['File']).toarray()

    return process_vec, file_vec
# 数据聚类
def cluster_data(process_vec, file_vec):
    combined_vec = np.hstack((process_vec, file_vec))
    mini_kmeans = MiniBatchKMeans(n_clusters=10, random_state=42)
    labels = mini_kmeans.fit_predict(combined_vec)
    centers = mini_kmeans.cluster_centers_
    return labels, centers

# 生成详细的规则
def generate_detailed_rules(data, labels):
    rules = {}
    for cluster_id in set(labels):
        cluster_data = data.iloc[labels == cluster_id]
        if not cluster_data.empty:
            process_rules = set(cluster_data['Process'].apply(lambda x: os.path.dirname(x) + '/*').unique())
            file_rules = set(cluster_data['File'].apply(lambda x: os.path.dirname(x) + '/*').unique())
            rules[cluster_id] = (process_rules, file_rules)
    return rules

# 删除冗余规则
def remove_redundant_rules(rules):
    final_rules = []
    for process_rules, file_rules in rules.values():
        simplified_file_rules = simplify_rules(file_rules)
        for process_rule in process_rules:
            final_rules.append((process_rule, simplified_file_rules))
    return final_rules

# 简化规则集
def simplify_rules(rules):
    sorted_rules = sorted(rules, key=lambda x: x.count('/'), reverse=False)
    simplified_rules = set()
    for rule in sorted_rules:
        if not any(fnmatch.fnmatch(rule, f"{existing_rule}/*") for existing_rule in simplified_rules):
            simplified_rules.add(rule)
    return simplified_rules

# 计算覆盖率
def calculate_coverage(data, rules):
    matches = 0
    for _, row in data.iterrows():
        for process_rule, file_rules in rules:
            if fnmatch.fnmatch(row['Process'], process_rule) and any(fnmatch.fnmatch(row['File'], file_rule) for file_rule in file_rules):
                matches += 1
                break
    coverage = matches / len(data) * 100
    return coverage, matches


def visualize_clusters(process_vec, file_vec, labels, centers):
    """可视化聚类结果"""
    combined_vec = np.hstack((process_vec, file_vec))  # 合并进程和文件向量
    pca = PCA(n_components=2)
    # 对合并后的数据进行降维
    reduced_combined_data = pca.fit_transform(combined_vec)

    # 分别取出降维后的进程数据和文件数据
    reduced_process_data = reduced_combined_data[:len(process_vec)]
    reduced_file_data = reduced_combined_data[len(file_vec):]

    # 将质心通过相同的PCA对象进行降维
    reduced_centers = pca.transform(centers)
    plt.figure(figsize=(10, 6))

    # 绘制进程的聚类数据点
    process_scatter = plt.scatter(reduced_process_data[:, 0], reduced_process_data[:, 1], c=labels[:len(process_vec)], cmap='viridis',
                                  marker='o', label='Process')
    # 绘制文件的聚类数据点
    file_scatter = plt.scatter(reduced_file_data[:, 0], reduced_file_data[:, 1], c=labels[len(process_vec):], cmap='plasma', marker='x',
                               label='File')
    # 绘制质心
    centroids_scatter = plt.scatter(reduced_centers[:, 0], reduced_centers[:, 1], c='red', s=200, alpha=0.5,
                                    label='Centroids')
    # 添加图例，手动设置句柄和标签
    plt.legend(handles=[process_scatter, file_scatter, centroids_scatter], labels=['Process', 'File', 'Centroids'])
    # 显示图例
    plt.show()
    print(f"Reduced Process Data Shape: {reduced_process_data.shape}")
    print(f"Reduced File Data Shape: {reduced_file_data.shape}")


# 主函数
def main():
    file_path = 'file_path'  # 根据需要调整路径，如'/Users/ycc/Desktop/test_log2'
    data = load_data(file_path)
    process_vec, file_vec = vectorize_data(data)

    labels,centers = cluster_data(process_vec, file_vec)

    rules = generate_detailed_rules(data, labels)
    refined_rules = remove_redundant_rules(rules)
    coverage, matches = calculate_coverage(data, refined_rules)
    error_rate = (len(data) - matches) / len(data) * 100
    print("Generated Rules:")
    for process_rule, file_rules in refined_rules:
        for file_rule in file_rules:
            print(f"Process rule: {process_rule}, File rule: {file_rule}")
    print(f"Coverage: {coverage:.2f}%")
    print(f"Matches: {matches} of {len(data)}")
    print(f"error: {error_rate:.2f}%")
    with open('last_daima_output.txt', 'w') as f:
        # 写入生成的规则
        for process_rule, file_rules in refined_rules:
            for file_rule in file_rules:
                f.write(f"Process rule: {process_rule}, File rule: {file_rule}\n")

        # 写入覆盖率和匹配数
        f.write(f"Coverage: {coverage:.2f}%\n")
        f.write(f"Error: {error_rate:.2f}%\n")
        f.write(f"Matches: {matches} of {len(data)}\n")
    # 将聚类结果可视化
    visualize_clusters(process_vec, file_vec, labels, centers)

if __name__ == "__main__":
    main()