import time
from concurrent.futures import ThreadPoolExecutor

def sum_square(x: int) -> int:
  final = 0
  for i in range(x):
    final += i * i
  return final


# if __name__ == "__main__":
#   start = time.perf_counter()
  
#   sum_square(100_000_000)
  
#   finish = time.perf_counter()
#   print(f"Finished in {round(finish-start, 2)} seconds")

if __name__ == "__main__":
  start = time.perf_counter()
  
  with ThreadPoolExecutor(8) as executor:
    results = executor.map(sum_square, [100_000_000])
  
  finish = time.perf_counter()
  print(f"Finished in {round(finish-start, 2)} seconds")  