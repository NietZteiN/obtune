/*The FibFib number sequence is a sequence similar to the Fibbonacci sequnece that's defined as follows:
  fibfib(0) == 0
  fibfib(1) == 0
  fibfib(2) == 1
  fibfib(n) == fibfib(n-1) + fibfib(n-2) + fibfib(n-3).
  Please write a function to efficiently compute the n-th element of the fibfib number sequence.
  >>> fibfib(1)
  0
  >>> fibfib(5)
  4
  >>> fibfib(8)
  24
  */
const fibfib = (n) => {

  if (n == 0 || n == 1)
    return 0;
  if (n == 2)
    return 1;
  return fibfib(n - 1) + fibfib(n - 2) + fibfib(n - 3);
}

const testFibfib = () => {
  console.assert(fibfib(2) === 1)
  console.assert(fibfib(1) === 0)
  console.assert(fibfib(5) === 4)
  console.assert(fibfib(8) === 24)
  console.assert(fibfib(10) === 81)
  console.assert(fibfib(12) === 274)
  console.assert(fibfib(14) === 927)
}

testFibfib()
