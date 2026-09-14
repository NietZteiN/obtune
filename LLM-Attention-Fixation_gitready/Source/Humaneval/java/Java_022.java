import java.util.*;
import java.lang.*;

class Solution {
    /**
    Filter given list of any values only for integers
    >>> filter_integers(Arrays.asList('a', 3.14, 5))
    [5]
    >>> filter_integers(Arrays.asList(1, 2, 3, "abc", Map.of(), List.of()))
    [1, 2, 3]
     */
    public List<Integer> filterIntergers(List<Object> values) {

        List<Integer> result = new ArrayList<>();
        for (Object x : values) {
            if (x instanceof Integer) {
                result.add((Integer) x);
            }
        }
        return result;
    }
}

public class Java_022 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.filterIntergers(new ArrayList<>(List.of())).equals(List.of()),
                s.filterIntergers(new ArrayList<>(Arrays.asList(4, Map.of(), List.of(), 23.2, 9, "adasd"))).equals(Arrays.asList(4, 9)),
                s.filterIntergers(new ArrayList<>(Arrays.asList(3, 'c', 3, 3, 'a', 'b'))).equals(Arrays.asList(3, 3, 3))
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
