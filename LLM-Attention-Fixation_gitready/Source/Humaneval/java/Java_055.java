import java.util.*;
import java.lang.*;

class Solution {
    /**
    Return n-th Fibonacci number.
    >>> fib(10)
    55
    >>> fib(1)
    1
    >>> fib(8)
    21
     */
    public int fib(int n) {

        if (n == 0) {
            return 0;
        }
        if (n == 1) {
            return 1;
        }
        return fib(n - 1) + fib(n - 2);
    }
}

public class Java_055 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.fib(10) == 55,
                s.fib(1) == 1,
                s.fib(8) == 21,
                s.fib(11) == 89,
                s.fib(12) == 144
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
