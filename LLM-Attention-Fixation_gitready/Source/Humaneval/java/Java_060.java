import java.util.*;
import java.lang.*;

class Solution {
    /**
    sumToN is a function that sums numbers from 1 to n.
    >>> sumToN(30)
    465
    >>> sumToN(100)
    5050
    >>> sumToN(5)
    15
    >>> sumToN(10)
    55
    >>> sumToN(1)
    1
     */
    public int sumToN(int n) {

        int result = 0;
        for (int i = 1; i <= n; i++) {
            result += i;
        }
        return result;
    }
}

public class Java_060 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.sumToN(1) == 1,
                s.sumToN(6) == 21,
                s.sumToN(11) == 66,
                s.sumToN(30) == 465,
                s.sumToN(100) == 5050
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
