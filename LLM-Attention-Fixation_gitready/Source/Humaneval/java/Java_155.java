import java.util.*;
import java.lang.*;

class Solution {
    /**
    Given an integer. return a tuple that has the number of even and odd digits respectively.
    
     Example:
        evenOddCount(-12) ==> (1, 1)
        evenOddCount(123) ==> (1, 2)
     */
    public List<Integer> evenOddCount(int num) {

        int even_count = 0, odd_count = 0;
        for (char i : String.valueOf(Math.abs(num)).toCharArray()) {
            if ((i - '0') % 2 == 0) {
                even_count += 1;
            } else {
                odd_count += 1;
            }
        }
        return Arrays.asList(even_count, odd_count);
    }
}

public class Java_155 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.evenOddCount(7).equals(Arrays.asList(0, 1)),
                s.evenOddCount(-78).equals(Arrays.asList(1, 1)),
                s.evenOddCount(3452).equals(Arrays.asList(2, 2)),
                s.evenOddCount(346211).equals(Arrays.asList(3, 3)),
                s.evenOddCount(-345821).equals(Arrays.asList(3, 3)),
                s.evenOddCount(-2).equals(Arrays.asList(1, 0)),
                s.evenOddCount(-45347).equals(Arrays.asList(2, 3)),
                s.evenOddCount(0).equals(Arrays.asList(1, 0))
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
