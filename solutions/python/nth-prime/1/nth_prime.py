def prime(n):
    if n < 1:
        raise ValueError("there is no zeroth prime")

    if n == 1:
        return 2

    count = 1      
    candidate = 3 

    while True:
        if is_prime(candidate):
            count += 1
            if count == n:
                return candidate
        candidate += 2  


def is_prime(num):
    limit = int(num ** 0.5) + 1
    for divisor in range(3, limit, 2):
        if num % divisor == 0:
            return False
    return True
