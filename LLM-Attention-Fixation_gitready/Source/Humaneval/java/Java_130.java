import java.util.*;
import java.lang.*;

class Solution {
    /**
    Everyone knows Fibonacci sequence, it was studied deeply by mathematicians in
    the last couple centuries. However, what people don't know is Tribonacci sequence.
    Tribonacci sequence is defined by the recurrence:
    tri(1) = 3
    tri(n) = 1 + n / 2, if n is even.
    tri(n) =  tri(n - 1) + tri(n - 2) + tri(n + 1), if n is odd.
    For example:
    tri(2) = 1 + (2 / 2) = 2
    tri(4) = 3
    tri(3) = tri(2) + tri(1) + tri(4)
           = 2 + 3 + 3 = 8
    You are given a non-negative integer number n, you have to a return a list of the
    first n + 1 numbers of the Tribonacci sequence.
    Examples:
    tri(3) = [1, 3, 2, 8]
     */
    public List<Integer> tri(int n) {

        if (n == 0) {
            return List.of(1);
        }
        List<Integer> my_tri = new ArrayList<>(Arrays.asList(1, 3));
        for (int i = 2; i <= n; i++) {
            if (i % 2 == 0) {
                my_tri.add(i / 2 + 1);
            } else {
                my_tri.add(my_tri.get(my_tri.size() - 1) + my_tri.get(my_tri.size() - 2) + (i + 3) / 2);
            }
        }
        return my_tri;
    }
}

public class Java_130 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.tri(3).equals(Arrays.asList(1, 3, 2, 8)),
                s.tri(4).equals(Arrays.asList(1, 3, 2, 8, 3)),
                s.tri(5).equals(Arrays.asList(1, 3, 2, 8, 3, 15)),
                s.tri(6).equals(Arrays.asList(1, 3, 2, 8, 3, 15, 4)),
                s.tri(7).equals(Arrays.asList(1, 3, 2, 8, 3, 15, 4, 24)),
                s.tri(8).equals(Arrays.asList(1, 3, 2, 8, 3, 15, 4, 24, 5)),
                s.tri(9).equals(Arrays.asList(1, 3, 2, 8, 3, 15, 4, 24, 5, 35)),
                s.tri(20).equals(Arrays.asList(1, 3, 2, 8, 3, 15, 4, 24, 5, 35, 6, 48, 7, 63, 8, 80, 9, 99, 10, 120, 11)),
                s.tri(0).equals(List.of(1)),
                s.tri(1).equals(Arrays.asList(1, 3))
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
