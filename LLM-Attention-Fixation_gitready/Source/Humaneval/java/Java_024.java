import java.util.*;
import java.lang.*;

class Solution {
    /**
    For a given number n, find the largest number that divides n evenly, smaller than n
    >>> largestDivisor(15)
    5
     */
    public int largestDivisor(int n) {

        for (int i = n - 1; i > 0; i--) {
            if (n % i == 0) {
                return i;
            }
        }
        return 1;
    }
}

public class Java_024 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.largestDivisor(3) == 1,
                s.largestDivisor(7) == 1,
                s.largestDivisor(10) == 5,
                s.largestDivisor(100) == 50,
                s.largestDivisor(49) == 7
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
