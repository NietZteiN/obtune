import java.util.*;
import java.lang.*;

class Solution {
    /**
    Write a function which sorts the given list of integers
    in ascending order according to the sum of their digits.
    Note: if there are several items with similar sum of their digits,
    order them based on their index in original list.

    For example:
    >>> orderByPoints(Arrays.asList(1, 11, -1, -11, -12)) == [-1, -11, 1, -12, 11]
    >>> orderByPoints(Arrays.asList()) == []
     */
    public List<Integer> orderByPoints(List<Integer> nums) {

        List<Integer> result = new ArrayList<>(nums);
        result.sort((o1, o2) -> {
            int sum1 = 0;
            int sum2 = 0;

            for (int i = 0; i < String.valueOf(o1).length(); i++) {
                if (i != 0 || o1 >= 0) {
                    sum1 += (String.valueOf(o1).charAt(i) - '0' );
                    if (i == 1 && o1 < 0) {
                        sum1 = -sum1;
                    }
                }
            }
            for (int i = 0; i < String.valueOf(o2).length(); i++) {
                if (i != 0 || o2 >= 0) {
                    sum2 += (String.valueOf(o2).charAt(i) - '0' );
                    if (i == 1 && o2 < 0) {
                        sum2 = -sum2;
                    }
                }
            }
            return Integer.compare(sum1, sum2);
        });
        return result;
    }
}

public class Java_145 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.orderByPoints(new ArrayList<>(Arrays.asList(1, 11, -1, -11, -12))).equals(Arrays.asList(-1, -11, 1, -12, 11)),
                s.orderByPoints(new ArrayList<>(Arrays.asList(1234, 423, 463, 145, 2, 423, 423, 53, 6, 37, 3457, 3, 56, 0, 46))).equals(Arrays.asList(0, 2, 3, 6, 53, 423, 423, 423, 1234, 145, 37, 46, 56, 463, 3457)),
                s.orderByPoints(new ArrayList<>(List.of())).equals(List.of()),
                s.orderByPoints(new ArrayList<>(Arrays.asList(1, -11, -32, 43, 54, -98, 2, -3))).equals(Arrays.asList(-3, -32, -98, -11, 1, 2, 43, 54)),
                s.orderByPoints(new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))).equals(Arrays.asList(1, 10, 2, 11, 3, 4, 5, 6, 7, 8, 9)),
                s.orderByPoints(new ArrayList<>(Arrays.asList(0, 6, 6, -76, -21, 23, 4))).equals(Arrays.asList(-76, -21, 0, 4, 23, 6, 6))
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
