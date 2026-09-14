import java.util.*;
import java.lang.*;

class Solution {
    /**
    Given a non-empty list of integers, return the sum of all of the odd elements that are in even positions.

    Examples
    solution(Arrays.asList(5, 8, 7, 1)) ==> 12
    solution(Arrays.asList(3, 3, 3, 3, 3)) ==> 9
    solution(Arrays.asList(30, 13, 24, 321)) ==>0
     */
    public int solution(List<Integer> lst) {

        int sum = 0;
        for (int i = 0; i < lst.size(); i += 2) {
            if ((lst.get(i) % 2) == 1) {
                sum += lst.get(i);
            }
        }
        return sum;
    }
}

public class Java_121 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.solution(Arrays.asList(5, 8, 7, 1)) == 12,
                s.solution(Arrays.asList(3, 3, 3, 3, 3)) == 9,
                s.solution(Arrays.asList(30, 13, 24, 321)) == 0,
                s.solution(Arrays.asList(5, 9)) == 5,
                s.solution(Arrays.asList(2, 4, 8)) == 0,
                s.solution(Arrays.asList(30, 13, 23, 32)) == 23,
                s.solution(Arrays.asList(3, 13, 2, 9)) == 3
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
