import java.util.*;
import java.lang.*;

class Solution {
    /**
    Return sorted unique common elements for two lists.
    >>> common(Arrays.asList(1, 4, 3, 34, 653, 2, 5), Arrays.asList(5, 7, 1, 5, 9, 653, 121))
    [1, 5, 653]
    >>> common(Arrays.asList(5, 3, 2, 8), Arrays.asList(3, 2))
    [2, 3]
     */
    public List<Integer> common(List<Integer> l1, List<Integer> l2) {

        Set<Integer> ret = new HashSet<>(l1);
        ret.retainAll(new HashSet<>(l2));
        List<Integer> result = new ArrayList<>(ret);
        Collections.sort(result);
        return result;
    }
}

public class Java_058 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.common(new ArrayList<>(Arrays.asList(1, 4, 3, 34, 653, 2, 5)), new ArrayList<>(Arrays.asList(5, 7, 1, 5, 9, 653, 121))).equals(Arrays.asList(1, 5, 653)),
                s.common(new ArrayList<>(Arrays.asList(5, 3, 2, 8)), new ArrayList<>(Arrays.asList(3, 2))).equals(Arrays.asList(2, 3)),
                s.common(new ArrayList<>(Arrays.asList(4, 3, 2, 8)), new ArrayList<>(Arrays.asList(3, 2, 4))).equals(Arrays.asList(2, 3, 4)),
                s.common(new ArrayList<>(Arrays.asList(4, 3, 2, 8)), new ArrayList<>(List.of())).equals(List.of())
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
