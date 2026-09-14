import java.util.*;
import java.lang.*;

class Solution {
    /**
    Given a list of positive integers x. return a sorted list of all
    elements that hasn't any even digit.

    Note: Returned list should be sorted in increasing order.
    
    For example:
    >>> uniqueDigits(Arrays.asList(15, 33, 1422, 1))
    [1, 15, 33]
    >>> uniqueDigits(Arrays.asList(152, 323, 1422, 10))
    []
     */
    public List<Integer> uniqueDigits(List<Integer> x) {

        List<Integer> odd_digit_elements = new ArrayList<>();
        for (int i : x) {
            boolean is_unique = true;
            for (char c : String.valueOf(i).toCharArray()) {
                if ((c - '0') % 2 == 0) {
                    is_unique = false;
                    break;
                }
            }
            if (is_unique) {
                odd_digit_elements.add(i);
            }
        }
        Collections.sort(odd_digit_elements);
        return odd_digit_elements;
    }
}

public class Java_104 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.uniqueDigits(Arrays.asList(15, 33, 1422, 1)).equals(Arrays.asList(1, 15, 33)),
                s.uniqueDigits(Arrays.asList(152, 323, 1422, 10)).equals(List.of()),
                s.uniqueDigits(Arrays.asList(12345, 2033, 111, 151)).equals(Arrays.asList(111, 151)),
                s.uniqueDigits(Arrays.asList(135, 103, 31)).equals(Arrays.asList(31, 135))
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
