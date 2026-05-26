from lot_1 import kmers,count_kmer_frequencies
from Bloum import BloomFilter

FASTA_FILE = "output/filtered_reads.fasta"
solidity_parameter = 125
k=5

def read_fasta(filepath):
    reads = []
    with open(filepath, "r") as file:
        while True:
            header = file.readline().strip()
            if not header:
                break
            seq = file.readline().strip()
            reads.append({
                "id": header,
                "sequence": seq
            })
    return reads


def solid_kmers(counts, solidity_parameter):
    solid = []
    for kmer, freq in counts.items():
        if freq >= solidity_parameter:
            solid.append(kmer)
    return solid


def extend_kmer(kmer, base):
    return kmer[1:] + base


def on_the_fly(seed, bloom, k, max_steps=50):
    contigs = []

    def exploration(current, path, visited):
        if len(path) >= max_steps:
            contigs.append(path)
            return

        visited.add(current)
        neighbors = []

        for base in "ACGT":
            next_kmer = extend_kmer(current, base)
            if bloom.contains(next_kmer):
                neighbors.append(next_kmer)

        if len(neighbors) == 0:
            contigs.append(path)
            return

        if len(neighbors) > 1:
            contigs.append(path)
            for n in neighbors:
                exploration(n, path + n[-1], visited.copy())
        else:
            n = neighbors[0]
            exploration(n, path + n[-1], visited)

    exploration(seed, seed, set())
    return contigs

reads = read_fasta(FASTA_FILE)
all_kmers = kmers(reads, k)
kmers_frequencies = count_kmer_frequencies(all_kmers)
solid_kmers_list = solid_kmers(kmers_frequencies, solidity_parameter)

bf = BloomFilter(size=1000, hash_count=3)
for kmer in solid_kmers_list:
    bf.add(kmer)

print("Nombre de k-mers solides:", len(solid_kmers_list))

if len(solid_kmers_list) > 0:
    seed = solid_kmers_list[0]
    contigs = on_the_fly(seed, bf, k)
    for c in contigs:
        print("CONTIG:", c)