# compare_algorithms.py
"""
Сравнительный анализ алгоритмов фаззи-хеширования:
- Ваш метод (SimHash + N-grams)
- ssdeep
- TLSH
"""

import json
from pathlib import Path
from dataset import generate_pairs
from evaluate import evaluate_pairs
from external_hashes import SSDeepAdapter, TLSHAdapter, CustomAdapter

# Проверка доступности библиотек
try:
    import ssdeep
    SSDEEP_AVAILABLE = True
except ImportError:
    SSDEEP_AVAILABLE = False
    print("Предупреждение: ssdeep не установлен. Пропускаем этот метод.")

try:
    import tlsh
    TLSH_AVAILABLE = True
except ImportError:
    TLSH_AVAILABLE = False
    print("Предупреждение: TLSH не установлен. Пропускаем этот метод.")


def main():
    print("=" * 70)
    print("СРАВНИТЕЛЬНЫЙ АНАЛИЗ АЛГОРИТМОВ ФАЗЗИ-ХЕШИРОВАНИЯ")
    print("=" * 70)

    # Параметры
    source_dir = "./scripts/white"   # ваша директория с исходным кодом
    output_dir = "./generated"
    thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]

    # 1. Генерация тестовых данных (один раз для всех алгоритмов)
    print("\n1. Генерация тестовых данных...")
    pairs = generate_pairs(
        source_dir=source_dir,
        output_dir=output_dir,
        max_files=50,       # можно увеличить для более точных результатов
        mods_per_file=3,
    )
    print(f"   Сгенерировано пар: {len(pairs)}")

    # 2. Подготовка алгоритмов
    algorithms = []

    # Ваш метод
    algorithms.append({
        "name": "Our Method",
        "build": CustomAdapter.build_signature,
        "compare": CustomAdapter.compare,
    })

    # ssdeep
    if SSDEEP_AVAILABLE:
        algorithms.append({
            "name": "ssdeep",
            "build": SSDeepAdapter.build_signature,
            "compare": SSDeepAdapter.compare,
        })

    # TLSH
    if TLSH_AVAILABLE:
        algorithms.append({
            "name": "TLSH",
            "build": TLSHAdapter.build_signature,
            "compare": TLSHAdapter.compare,
        })

    if len(algorithms) <= 1:
        print("Ошибка: нет доступных алгоритмов для сравнения.")
        return

    # 3. Оценка каждого алгоритма
    print("\n2. Оценка алгоритмов...")
    all_results = {}

    for algo in algorithms:
        name = algo["name"]
        print(f"\n   Оценка: {name}")

        best_f1 = 0.0
        best_th = 0.0
        best_metrics = None

        for th in thresholds:
            report = evaluate_pairs(
                pairs=pairs,
                threshold=th,
                build_sig_fn=algo["build"],
                compare_sig_fn=algo["compare"],
            )
            metrics = report["metrics"]
            f1 = metrics["f1"]

            if f1 > best_f1:
                best_f1 = f1
                best_th = th
                best_metrics = metrics

            print(f"      threshold={th:.1f}: P={metrics['precision']:.3f}, "
                  f"R={metrics['recall']:.3f}, F1={f1:.3f}, "
                  f"FPR={metrics['false_positive_rate']:.3f}")

        all_results[name] = {
            "best_threshold": best_th,
            "best_metrics": best_metrics,
            "all_thresholds": {
                th: evaluate_pairs(
                    pairs=pairs,
                    threshold=th,
                    build_sig_fn=algo["build"],
                    compare_sig_fn=algo["compare"],
                )["metrics"]
                for th in thresholds
            }
        }

    # 4. Итоговая таблица
    print("\n" + "=" * 70)
    print("СВОДНАЯ ТАБЛИЦА (лучшие результаты по F1)")
    print("=" * 70)

    header = f"{'Algorithm':<15} | {'Threshold':<10} | {'Precision':<10} | {'Recall':<10} | {'F1':<10} | {'FPR':<10} | {'FNR':<10}"
    print(header)
    print("-" * len(header))

    for name, data in all_results.items():
        m = data["best_metrics"]
        th = data["best_threshold"]
        print(f"{name:<15} | {th:<10.2f} | {m['precision']:<10.4f} | "
              f"{m['recall']:<10.4f} | {m['f1']:<10.4f} | "
              f"{m['false_positive_rate']:<10.4f} | {m['false_negative_rate']:<10.4f}")

    # 5. Сохранение результатов в JSON
    output_path = Path("comparison_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nРезультаты сохранены в {output_path}")

    # 6. Визуализация (если matplotlib доступен)
    try:
        import matplotlib.pyplot as plt
        import numpy as np

        plt.figure(figsize=(10, 6))

        for name, data in all_results.items():
            th_vals = sorted(data["all_thresholds"].keys())
            f1_vals = [data["all_thresholds"][th]["f1"] for th in th_vals]
            plt.plot(th_vals, f1_vals, marker='o', label=name)

        plt.xlabel("Threshold")
        plt.ylabel("F1-score")
        plt.title("Сравнение алгоритмов: F1-score в зависимости от порога")
        plt.legend()
        plt.grid(True)
        plt.savefig("comparison_f1.png", dpi=150)
        plt.show()

        # ROC-подобный график (FPR vs Recall)
        plt.figure(figsize=(10, 6))
        for name, data in all_results.items():
            th_vals = sorted(data["all_thresholds"].keys())
            fpr_vals = [data["all_thresholds"][th]["false_positive_rate"] for th in th_vals]
            recall_vals = [data["all_thresholds"][th]["recall"] for th in th_vals]
            plt.plot(fpr_vals, recall_vals, marker='o', label=name)

        plt.xlabel("False Positive Rate (FPR)")
        plt.ylabel("Recall")
        plt.title("Сравнение алгоритмов: ROC-подобный график")
        plt.legend()
        plt.grid(True)
        plt.savefig("comparison_roc.png", dpi=150)
        plt.show()

    except ImportError:
        print("matplotlib не установлен. Графики не построены.")

    print("\nСравнение завершено.")


if __name__ == "__main__":
    main()