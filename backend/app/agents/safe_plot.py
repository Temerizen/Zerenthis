import matplotlib
import matplotlib.pyplot as plt
import warnings
import unicodedata
import tempfile
import os
import sys

# ===============================
# 1. Global safe configuration
# ===============================
# Use a font with extremely broad Unicode coverage
matplotlib.rcParams['font.family'] = 'Noto Sans'  # robust Unicode font
matplotlib.rcParams['axes.unicode_minus'] = True
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# Suppress all user warnings from matplotlib
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# ===============================
# 2. Safe text cleaning function
# ===============================
def clean_text(text):
    """
    Cleans any string to be safe for matplotlib plotting.
    - Replaces control characters (like \x85) with space.
    - Normalizes Unicode.
    - Converts None to empty string.
    """
    if text is None:
        return ""
    text = str(text)  # ensure string
    text = unicodedata.normalize('NFKD', text)
    # Replace all control characters with a safe space
    safe_text = ''.join(c if unicodedata.category(c)[0] != 'C' else ' ' for c in text)
    return safe_text

# ===============================
# 3. Foolproof plot saving function
# ===============================
def save_plot(x, y, title="", xlabel="", ylabel="", filename=None, figsize=(8,6)):
    """
    Creates and saves a plot safely:
    - All text cleaned
    - Automatically closes figure to avoid memory leaks
    - Saves to temporary file if filename not provided
    """
    title = clean_text(title)
    xlabel = clean_text(xlabel)
    ylabel = clean_text(ylabel)

    plt.figure(figsize=figsize)
    plt.plot(x, y, marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)

    if filename is None:
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        filename = tmp_file.name
        tmp_file.close()  # we only need the path
    else:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    try:
        plt.savefig(filename, bbox_inches='tight')
    except Exception as e:
        print(f"[Warning] Saving plot failed: {e}", file=sys.stderr)
        # fallback: save to temp file
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        filename = tmp_file.name
        tmp_file.close()
        plt.savefig(filename, bbox_inches='tight')

    plt.close()
    return filename

# ===============================
# 4. Example usage
# ===============================
if __name__ == "__main__":
    x = [1, 2, 3, 4]
    y = [10, 20, 15, 25]
    filename = save_plot(
        x, y,
        title="Perfect Plot – weird chars \x85 \x91 \u200b",
        xlabel="X-axis \x85 label",
        ylabel="Y-axis \x85 label"
    )
    print(f"Plot saved to: {filename}")