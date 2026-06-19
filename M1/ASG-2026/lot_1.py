import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template
from collections import Counter
import matplotlib.pyplot as plt

app = Flask(__name__)

FASTQ_FILE = "input/1_control_psbA3_2019_minq7.fastq"

K = 5
seuil_erreur = 0.10

def read_fastq(filepath):
    reads = []
    with open(filepath, "r") as file:
        while True:
            header = file.readline().strip()

            if not header:
                break

            seq = file.readline().strip()
            plus = file.readline().strip()
            qual = file.readline().strip()

            reads.append({
                "id": header,
                "sequence": seq,
                "quality": qual
            })
    return reads


def phred_score(char):
    return ord(char) - 33


def average_error_rate(quality_string):
    probs = []
    for c in quality_string:
        q = phred_score(c)
        p = 10 ** (-q / 10)
        probs.append(p)
    if len(probs) == 0:
        return 0
    return sum(probs) / len(probs)


def filter_reads(reads, seuil_erreur):
    filtered = []
    for read in reads:
        error = average_error_rate(read["quality"])
        if error <= seuil_erreur:
            filtered.append(read)
    return filtered


def export_fasta(reads, output_file):
    with open(output_file, "w") as fasta:
        for read in reads:
            fasta.write(f">{read['id'][1:]}\n")
            fasta.write(f"{read['sequence']}\n")


def extract_kmers(sequence, k):
    kmers = []
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i+k]
        kmers.append(kmer)
    return kmers


def kmers(reads, k):
    all_kmers = []
    for read in reads:
        kmers = extract_kmers(read["sequence"], k)
        all_kmers.extend(kmers)
    return all_kmers


def count_kmer_frequencies(all_kmers):
    return Counter(all_kmers)


def plot_histogram(frequencies):
    kmers = list(frequencies.keys())
    counts = list(frequencies.values())
    plt.figure(figsize=(12, 6))
    plt.bar(kmers, counts)
    plt.xlabel("K-mer")
    plt.ylabel("Nombre d'apparitions")
    plt.title("Fréquence de chaque k-mer")
    plt.xticks(rotation=90)  
    plt.tight_layout()
    plt.savefig("static/histogram.png")
    plt.close()


@app.route("/")
def index():
    reads = read_fastq(FASTQ_FILE)
    filtered_reads = filter_reads(reads, seuil_erreur)
    export_fasta(filtered_reads,"output/filtered_reads.fasta")
    all_kmers = kmers(filtered_reads, K)
    kmer_frequencies = count_kmer_frequencies(all_kmers)
    print(kmer_frequencies )
    plot_histogram(kmer_frequencies)

    total_error = 0
    for read in filtered_reads:
        error = average_error_rate(read["quality"])
        total_error += error

    if len(filtered_reads) > 0:
        average_error = (total_error / len(filtered_reads)) * 100
    else:
        average_error = 0

    return render_template(
        "index.html",
        total_reads=len(reads),
        filtered_reads=len(filtered_reads),
        total_kmers=len(all_kmers),
        unique_kmers=len(kmer_frequencies),
        average_error=average_error
    )


if __name__ == "__main__":
    app.run(debug=True)