import java.util.*;
import java.lang.*;

class Solution {
    /**
    Return the number of times the digit 7 appears in integers less than n which are divisible by 11 or 13.
    >>> fizzBuzz(50)
    0
    >>> fizzBuzz(78)
    2
    >>> fizzBuzz(79)
    3
     */
    public int fizzBuzz(int n) {

        int result = 0;
        for (int i = 1; i < n; i++) {
            if (i % 11 == 0 || i % 13 == 0) {
                char[] digits = String.valueOf(i).toCharArray();
                for (char c : digits) {
                    if (c == '7') {
                        result += 1;
                    }
                }
            }
        }
        return result;
    }
}

public class Java_036 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.fizzBuzz(50) == 0,
                s.fizzBuzz(78) == 2,
                s.fizzBuzz(79) == 3,
                s.fizzBuzz(100) == 3,
                s.fizzBuzz(200) == 6,
                s.fizzBuzz(4000) == 192,
                s.fizzBuzz(10000) == 639,
                s.fizzBuzz(100000) == 8026
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
