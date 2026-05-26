def partitions(n, max, partition_courante, result):
    if n == 0:
        result.append(partition_courante[:])
        return
    for i in range(min(n, max), 0, -1):
        partition_courante.append(i)
        partitions(n - i, i, partition_courante, result)
        partition_courante.pop()

n = 3
result = []
partitions(n, n, [], result)
print(result)