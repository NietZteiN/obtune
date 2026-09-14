import java.util.*;
import java.lang.*;

class Solution {
    /**
    Given a list of numbers, return the sum of squares of the numbers
    in the list that are odd. Ignore numbers that are negative or not integers.

    doubleTheDifference(Arrays.asList(1, 3, 2, 0)) == 1 + 9 + 0 + 0 = 10
    doubleTheDifference(Arrays.asList(-1, -2, 0)) == 0
    doubleTheDifference(Arrays.asList(9, -2)) == 81
    doubleTheDifference(Arrays.asList(0)) == 0

    If the input list is empty, return 0.
     */
    public int doubleTheDifference(List<Object> lst) {

        return lst.stream().filter(i -> i instanceof Integer p && p > 0 && p % 2 != 0).map(i -> (Integer) i * (Integer) i).reduce(Integer::sum).orElse(0);
    }
}

public class Java_151 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.doubleTheDifference(List.of()) == 0,
                s.doubleTheDifference(Arrays.asList(5, 4)) == 25,
                s.doubleTheDifference(Arrays.asList(0.1, 0.2, 0.3)) == 0,
                s.doubleTheDifference(Arrays.asList(-10, -20, -30)) == 0,
                s.doubleTheDifference(Arrays.asList(-1, -2, 8)) == 0,
                s.doubleTheDifference(Arrays.asList(0.2, 3, 5)) == 34
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
        List<Object> lst = new ArrayList<>();
        for (int i = -99; i < 100; i += 2) {
            lst.add(i);
        }
        int odd_sum = lst.stream().filter(i -> i instanceof Integer p && p % 2 != 0 && p > 0).map(i -> (Integer) i * (Integer) i).reduce(Integer::sum).orElse(0);
        assert s.doubleTheDifference(lst) == odd_sum;
    }
}
