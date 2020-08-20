cache = [0, 1, 2]


def fibo(n):
    if n < 2:
        return n

    global cache
    for i in range(3, n + 1):
        cache[i] = cache[i - 1] + cache[i - 2]
    return cache[n]


inputs = input('').split(' ')
n = int(inputs[0])
k = int(inputs[1])
if n > len(cache):
    cache.extend([0 for _ in range(n-len(cache)+1)])
A_sum = 0
for i in range(1, n + 1):
    A_sum += fibo(i) * (i ** k)

print(A_sum % (10 ** 9 + 7))