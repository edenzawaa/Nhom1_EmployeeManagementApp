import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

CSV_FILE = "face_embeddings.csv"


def load_embeddings():
    df = pd.read_csv(CSV_FILE)
    # --- THIS IS THE FIX ---
    names = df["label"]
    embeddings = df.drop(columns=["label"]).values
    # ---------------------
    return names, embeddings


def visualize_2d(names, embeddings, use_tsne=False):
    if use_tsne:
        n_samples = len(embeddings)
        perplexity = max(1, min(30, n_samples - 1))

        reducer = TSNE(
            n_components=2,
            perplexity=perplexity,
            learning_rate="auto",
            init="pca"
        )
        title = f"t-SNE 2D Embedding Visualization (perplexity={perplexity})"
    else:
        reducer = PCA(n_components=2)
        title = "PCA 2D Embedding Visualization"

    reduced = reducer.fit_transform(embeddings)

    plt.figure(figsize=(8, 6))
    unique_names = list(set(names))

    for person in unique_names:
        idxs = [i for i, n in enumerate(names) if n == person]
        plt.scatter(reduced[idxs, 0], reduced[idxs, 1], label=person)

    plt.title(title)
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.legend()
    plt.grid(True)
    plt.savefig("embedding_plot.png")
    print("Saved plot to png")

def visualize_3d(names, embeddings):
    pca = PCA(n_components=3)
    reduced = pca.fit_transform(embeddings)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    unique_names = list(set(names))

    for person in unique_names:
        idxs = [i for i, n in enumerate(names) if n == person]
        ax.scatter(
            reduced[idxs, 0],
            reduced[idxs, 1],
            reduced[idxs, 2],
            label=person
        )

    ax.set_title("PCA 3D Embedding Visualization")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_zlabel("PC3")
    ax.legend()
    plt.savefig("embedding_plot.png")
    print("Saved plot to png")



def main():
    names, embeddings = load_embeddings()

    print("Visualization options:")
    print("1. PCA 2D")
    print("2. t-SNE 2D")
    print("3. PCA 3D")
    choice = input("Choose (1/2/3): ")

    if choice == "1":
        visualize_2d(names, embeddings, use_tsne=False)
    elif choice == "2":
        visualize_2d(names, embeddings, use_tsne=True)
    elif choice == "3":
        visualize_3d(names, embeddings)
    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()