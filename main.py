from dataset import generate_pairs
from evaluate import evaluate_pairs
from visualize import compute_roc, plot_roc, plot_similarity_histogram


def main():
    source_dir = "./scripts/white"   # директория с исходным кодом
    output_dir = "./generated"

    print("Генерация тестовых данных...")
    pairs = generate_pairs(
        source_dir=source_dir,
        output_dir=output_dir,
        max_files=200,
        mods_per_file=2,
    )

    print(f"Сгенерировано пар: {len(pairs)}")

    print("\nЗапуск оценки...")
    report = evaluate_pairs(pairs, threshold=0.7, save_normalized=True, normalized_dir="./normalized")

    metrics = report["metrics"]

    print("\n=== РЕЗУЛЬТАТЫ ===")
    print(f"Всего пар:\t{report['total_pairs']}")
    print(f"Precision:\t{metrics['precision']}")
    print(f"Recall:\t\t{metrics['recall']}")
    print(f"F1-score:\t{metrics['f1']}")
    print(f"Accuracy:\t{metrics['accuracy']}")
    print(f"FPR:\t\t{metrics['false_positive_rate']}")
    print(f"FNR:\t\t{metrics['false_negative_rate']}")

    # plot_similarity_histogram(report["results"])

    # thresholds = [i / 20 for i in range(1, 20)]  # 0.05 ... 0.95
    # fpr, tpr = compute_roc(pairs, thresholds)
    #
    # plot_roc(fpr, tpr, title="ROC for fuzzy code similarity")


if __name__ == "__main__":
    main()
