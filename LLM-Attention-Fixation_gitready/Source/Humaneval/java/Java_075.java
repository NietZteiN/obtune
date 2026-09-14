import java.util.*;
import java.lang.*;

class Solution {
    /**
    Write a function that returns true if the given number is the multiplication of 3 prime numbers
    and false otherwise.
    Knowing that (a) is less then 100.
    Example:
    isMultiplyPrime(30) == true
    30 = 2 * 3 * 5
     */
    public boolean isMultiplyPrime(int a) {

        class IsPrime {
            public static boolean is_prime(int n) {
                for (int j = 2; j < n; j++) {
                    if (n % j == 0) {
                        return false;
                    }
                }
                return true;
            }
        }
        for (int i = 2; i < 101; i++) {
            if (!IsPrime.is_prime(i)) {
                continue;
            }
            for (int j = i; j < 101; j++) {
                if (!IsPrime.is_prime(j)) {
                    continue;
                }
                for (int k = j; k < 101; k++) {
                    if (!IsPrime.is_prime(k)) {
                        continue;
                    }
                    if (i * j * k == a) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
}

public class Java_075 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                !s.isMultiplyPrime(5),
                s.isMultiplyPrime(30),
                s.isMultiplyPrime(8),
                !s.isMultiplyPrime(10),
                s.isMultiplyPrime(125),
                s.isMultiplyPrime(3 * 5 * 7),
                !s.isMultiplyPrime(3 * 6 * 7),
                !s.isMultiplyPrime(9 * 9 * 9),
                !s.isMultiplyPrime(11 * 9 * 9),
                s.isMultiplyPrime(11 * 13 * 7)
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
