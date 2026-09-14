import java.util.*;
import java.lang.*;

class Solution {
    /**
    In this Kata, you have to sort an array of non-negative integers according to
    number of ones in their binary representation in ascending order.
    For similar number of ones, sort based on decimal value.
    <p>
    It must be implemented like this:
    >>> sortArray(Arrays.asList(1, 5, 2, 3, 4)).equals(Arrays.asList(1, 2, 3, 4, 5))
    >>> sortArray(Arrays.asList(-2, -3, -4, -5, -6)).equals(Arrays.asList(-6, -5, -4, -3, -2))
    >>> sortArray(Arrays.asList(1, 0, 2, 3, 4)).equals(Arrays.asList(0, 1, 2, 3, 4))
     */
    public List<Integer> sortArray(List<Integer> arr) {

                List < Integer > sorted_arr = new ArrayList<>(arr);
        sorted_arr.sort(new Comparator<Integer>() {
            @Override
            public int compare(Integer o1, Integer o2) {
                int cnt1 = (int) Integer.toBinaryString(Math.abs(o1)).chars().filter(ch -> ch == '1').count();
                int cnt2 = (int) Integer.toBinaryString(Math.abs(o2)).chars().filter(ch -> ch == '1').count();
                if (cnt1 > cnt2) {
                    return 1;
                } else if (cnt1 < cnt2) {
                    return -1;
                } else {
                    return o1.compareTo(o2);
                }
            }
        });
        return sorted_arr;
    }
}

public class Java_116 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.sortArray(new ArrayList<>(Arrays.asList(1, 5, 2, 3, 4))).equals(Arrays.asList(1, 2, 4, 3, 5)),
                s.sortArray(new ArrayList<>(Arrays.asList(-2, -3, -4, -5, -6))).equals(Arrays.asList(-4, -2, -6, -5, -3)),
                s.sortArray(new ArrayList<>(Arrays.asList(1, 0, 2, 3, 4))).equals(Arrays.asList(0, 1, 2, 4, 3)),
                s.sortArray(new ArrayList<>(List.of())).equals(List.of()),
                s.sortArray(new ArrayList<>(Arrays.asList(2, 5, 77, 4, 5, 3, 5, 7, 2, 3, 4))).equals(Arrays.asList(2, 2, 4, 4, 3, 3, 5, 5, 5, 7, 77)),
                s.sortArray(new ArrayList<>(Arrays.asList(3, 6, 44, 12, 32, 5))).equals(Arrays.asList(32, 3, 5, 6, 12, 44)),
                s.sortArray(new ArrayList<>(Arrays.asList(2, 4, 8, 16, 32))).equals(Arrays.asList(2, 4, 8, 16, 32)),
                s.sortArray(new ArrayList<>(Arrays.asList(2, 4, 8, 16, 32))).equals(Arrays.asList(2, 4, 8, 16, 32))
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
