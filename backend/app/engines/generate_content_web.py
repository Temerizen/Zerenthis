# ==============================================
# generate_content_web.py
# LEVEL INFINITE AI STATION 2026 – Web Marketplace Ready
# ==============================================

import os, random, string, time, threading, csv, webbrowser
from datetime import datetime
import matplotlib, matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import warnings, unicodedata, tempfile

# ===============================
# 1. Safe plotting config
# ===============================
matplotlib.rcParams['font.family'] = ['Noto Sans', 'DejaVu Sans', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = True
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# ===============================
# 2. Clean text
# ===============================
def clean_text(text):
    if text is None: return ""
    text = str(text)
    text = unicodedata.normalize('NFKC', text)
    return ''.join(c if unicodedata.category(c)[0] != 'C' else ' ' for c in text)

# ===============================
# 3. Generate plot
# ===============================
def generate_plot(data, filename):
    x, y = data["x"], data["y"]
    chart_type = data["chart_type"]
    plt.figure(figsize=(8,6))
    color, marker, linestyle, alpha = random.choice(["skyblue","orange","green","purple","red","gold","pink"]), random.choice(["o","s","^","D","*"]), random.choice(["-","--","-.",":"]), random.uniform(0.6, 1.0)
    if chart_type == "line": plt.plot(x, y, color=color, marker=marker, linestyle=linestyle, alpha=alpha)
    elif chart_type == "bar": plt.bar(x, y, color=color, alpha=alpha)
    elif chart_type == "scatter": plt.scatter(x, y, c=color, s=random.randint(30,200), alpha=alpha)
    elif chart_type == "line+scatter":
        plt.plot(x, y, color=color, marker=marker, linestyle=linestyle, alpha=alpha)
        plt.scatter(x, y, c="black", s=random.randint(20,100), alpha=0.7)
    plt.title(clean_text(data["title"]))
    plt.xlabel(clean_text(data["xlabel"]))
    plt.ylabel(clean_text(data["ylabel"]))
    plt.grid(True)
    try: plt.savefig(filename, bbox_inches='tight')
    except:
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        filename = tmp_file.name
        tmp_file.close()
        plt.savefig(filename, bbox_inches='tight')
    plt.close()
    return filename

# ===============================
# 4. Random dataset
# ===============================
def generate_random_text(length=30):
    emojis = "😀😎😂🔥💥✨🌟💯🎉🤖💫🌈🛸💣🧬🕹️⚡🎯🎲"
    safe_chars = string.ascii_letters + string.digits + string.punctuation.replace('$','')
    zero_width = "\u200b\u200c\u200d\u2060"
    chars = safe_chars + emojis + zero_width
    return ''.join(random.choice(chars) for _ in range(length))

def generate_random_dataset(max_points=15):
    num_points = random.randint(3, max_points)
    x = list(range(num_points))
    y = [random.randint(0, 100) for _ in range(num_points)]
    chart_type = random.choice(["line","bar","scatter","line+scatter"])
    title = generate_random_text(30)
    xlabel = generate_random_text(15)
    ylabel = generate_random_text(15)
    return {"x":x,"y":y,"chart_type":chart_type,"title":title,"xlabel":xlabel,"ylabel":ylabel}

# ===============================
# 5. Directory management
# ===============================
def create_output_dir(base="output"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base, f"batch_{timestamp}")
    os.makedirs(os.path.join(output_dir,"plots"), exist_ok=True)
    os.makedirs(os.path.join(output_dir,"pdfs"), exist_ok=True)
    return output_dir

# ===============================
# 6. Generate PDF report
# ===============================
def generate_mass_plots(num_plots=50, output_dir=None, report_size="Medium"):
    if output_dir is None: output_dir=create_output_dir()
    plot_dir=os.path.join(output_dir,"plots")
    pdf_dir=os.path.join(output_dir,"pdfs")
    saved_files=[]
    timestamp=datetime.now().strftime("%Y%m%d_%H%M")
    pdf_file_path=os.path.join(pdf_dir,f"Report_{report_size}_{timestamp}.pdf")
    with PdfPages(pdf_file_path) as pdf:
        for i in range(1,num_plots+1):
            data=generate_random_dataset()
            filename=os.path.join(plot_dir,f"plot_{i}.png")
            generate_plot(data,filename)
            saved_files.append(filename)
            fig=plt.figure(figsize=(8,6))
            img=plt.imread(filename)
            plt.imshow(img)
            plt.axis("off")
            pdf.savefig(fig)
            plt.close(fig)
    return saved_files, output_dir, pdf_file_path

# ===============================
# 7. HTML gallery
# ===============================
def generate_html_gallery(saved_files, output_dir):
    html_file=os.path.join(output_dir,"index.html")
    with open(html_file,"w",encoding="utf-8") as f:
        f.write("<html><head><meta charset='UTF-8'><title>Batch Gallery</title>\n")
        f.write("<style>body{font-family:sans-serif;} img{max-width:400px;margin:5px;border:1px solid #ccc;} .plot{display:inline-block;text-align:center;margin:10px;}</style>\n")
        f.write("</head><body>\n")
        f.write(f"<h1>Batch Gallery ({len(saved_files)} plots)</h1>\n")
        for file_path in saved_files:
            fname=os.path.basename(file_path)
            f.write(f"<div class='plot'><h4>{fname}</h4><img src='plots/{fname}'/></div>\n")
        f.write("</body></html>\n")
    return html_file

# ===============================
# 8. Download link generator
# ===============================
def generate_download_link(pdf_file):
    abs_path=os.path.abspath(pdf_file)
    url_path=abs_path.replace("\\","/")
    return f"file:///{url_path}"

# ===============================
# 9. Inventory CSV
# ===============================
def update_inventory_with_link(pdf_file,size,num_plots,price):
    download_link=generate_download_link(pdf_file)
    inventory_file=os.path.join("output","report_inventory.csv")
    os.makedirs("output",exist_ok=True)
    exists=os.path.exists(inventory_file)
    with open(inventory_file,"a",newline="",encoding="utf-8") as csvfile:
        writer=csv.writer(csvfile)
        if not exists:
            writer.writerow(["Filename","Size","Timestamp","Plots","Price","Download_Link"])
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([pdf_file,size,timestamp,num_plots,price,download_link])
    return download_link

# ===============================
# 10. Price by size
# ===============================
def get_price(size):
    if size.lower()=="small": return 10
    elif size.lower()=="medium": return 35
    elif size.lower()=="large": return 100
    return 35

# ===============================
# 11. Generate report
# ===============================
def generate_report(size="medium"):
    if size=="small": num_plots=5
    elif size=="medium": num_plots=15
    elif size=="large": num_plots=30
    else: num_plots=15
    price=get_price(size)
    saved_files, output_dir, pdf_file=generate_mass_plots(num_plots=num_plots, report_size=size.capitalize())
    generate_html_gallery(saved_files, output_dir)
    link=update_inventory_with_link(pdf_file,size,num_plots,price)
    print(f"✅ {size.capitalize()} report ready: {pdf_file} | Price: ${price} | Download: {link}")
    return pdf_file

# ===============================
# 12. Command to generate your first report
# ===============================
if __name__=="__main__":
    print("🚀 Generating your first example report...")
    generate_report("medium")
    print("🎉 Done! Check output/ for PDF, gallery, and download link.")