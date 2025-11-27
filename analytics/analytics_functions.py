# analytics/analytics_functions.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Make charts folder if missing
BASE = os.path.dirname(__file__)
TASKS_CSV = os.path.join(BASE, "..", "data", "tasks.csv")
PROGRESS_CSV = os.path.join(BASE, "..", "data", "progress.csv")
CHARTS_DIR = os.path.join(BASE, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# Use larger fonts for nicer visuals
rcParams.update({
    "font.size": 12,
    "axes.titlesize": 16,
    "axes.labelsize": 12,
    "figure.figsize": (8, 5),
    "figure.dpi": 120,
})


def safe_read_csv(path):
    try:
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path)
        return df
    except Exception:
        return None


# ---------- Tasks per subject (bright bar) ----------
def tasks_per_subject_chart():
    df = safe_read_csv(TASKS_CSV)

    save_path = os.path.join(CHARTS_DIR, "tasks_per_subject.png")
    plt.close("all")

    if df is None or df.empty:
        fig = plt.figure()
        plt.text(0.5, 0.5, "No tasks data\nAdd tasks to see analytics",
                 ha="center", va="center", fontsize=14)
        plt.axis("off")
        fig.savefig(save_path, bbox_inches="tight", transparent=False)
        plt.close(fig)
        return save_path

    # prefer lowercase 'subject' column (your CSV uses 'subject')
    col = None
    for candidate in ["subject", "Subject", "category", "Category"]:
        if candidate in df.columns:
            col = candidate
            break

    if col is None:
        fig = plt.figure()
        plt.text(0.5, 0.5, "No 'subject' column found in tasks.csv",
                 ha="center", va="center", fontsize=14)
        plt.axis("off")
        fig.savefig(save_path, bbox_inches="tight", transparent=False)
        plt.close(fig)
        return save_path

    counts = df[col].fillna("Unknown").value_counts().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.Set3.colors  # bright pleasant palette
    bars = ax.barh(counts.index, counts.values, color=colors[: len(counts)])
    ax.set_title("Tasks per Subject")
    ax.set_xlabel("Number of tasks")
    ax.set_ylabel("Subject")
    ax.grid(axis="x", linestyle="--", alpha=0.3)

    # add numbers on bars
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.1, bar.get_y() + bar.get_height() / 2,
                str(int(w)), va="center", fontsize=11)

    fig.tight_layout()
    fig.savefig(save_path, bbox_inches="tight", transparent=False)
    plt.close(fig)
    return save_path


# ---------- Priority distribution (pie) ----------
def priority_distribution_chart():
    df = safe_read_csv(TASKS_CSV)
    save_path = os.path.join(CHARTS_DIR, "priority_distribution.png")
    plt.close("all")

    if df is None or df.empty or "priority" not in df.columns:
        fig = plt.figure()
        plt.text(0.5, 0.5, "No priority data available", ha="center", va="center", fontsize=14)
        plt.axis("off")
        fig.savefig(save_path, bbox_inches="tight", transparent=False)
        plt.close(fig)
        return save_path

    counts = df["priority"].fillna("Unknown").value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = plt.cm.Pastel1.colors
    ax.pie(counts.values, labels=counts.index, autopct="%1.0f%%", startangle=140, colors=colors)
    ax.set_title("Priority Distribution")
    fig.tight_layout()
    fig.savefig(save_path, bbox_inches="tight", transparent=False)
    plt.close(fig)
    return save_path


# ---------- Completion progress (line) ----------
def completion_progress_chart():
    df = safe_read_csv(PROGRESS_CSV)
    save_path = os.path.join(CHARTS_DIR, "completion_progress.png")
    plt.close("all")

    if df is None or df.empty or "Date" not in df.columns or "Completion" not in df.columns:
        fig = plt.figure()
        plt.text(0.5, 0.5, "No progress data yet\n(we'll create progress.csv automatically)",
                 ha="center", va="center", fontsize=14)
        plt.axis("off")
        fig.savefig(save_path, bbox_inches="tight", transparent=False)
        plt.close(fig)
        return save_path

    # convert Date to readable form if needed
    try:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
    except Exception:
        pass

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["Date"].astype(str), df["Completion"], marker="o", linewidth=2)
    ax.set_title("Completion Progress")
    ax.set_xlabel("Date")
    ax.set_ylabel("Completion (%)")
    ax.grid(True, linestyle="--", alpha=0.3)
    for x, y in zip(df["Date"].astype(str), df["Completion"]):
        ax.text(x, y + 1, str(y), ha="center", fontsize=9)

    plt.xticks(rotation=20)
    fig.tight_layout()
    fig.savefig(save_path, bbox_inches="tight", transparent=False)
    plt.close(fig)
    return save_path
