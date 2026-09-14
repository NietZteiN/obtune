import java.util.*;
import java.lang.*;

class Solution {
    /**
    You are given a list of integers.
    Write a function nextSmallest() that returns the 2nd smallest element of the list.
    Return null if there is no such element.
    <p>
    nextSmallest(Arrays.asList(1, 2, 3, 4, 5)) == Optional[2]
    nextSmallest(Arrays.asList(5, 1, 4, 3, 2)) == Optional[2]
    nextSmallest(Arrays.asList()) == Optional.empty
    nextSmallest(Arrays.asList(1, 1)) == Optional.empty
     */
    public Optional<Integer> nextSmallest(List<Integer> lst) {

                Set < Integer > set = new HashSet<>(lst);
        List<Integer> l = new ArrayList<>(set);
        Collections.sort(l);
        if (l.size() < 2) {
            return Optional.empty();
        } else {
            return Optional.of(l.get(1));
        }
    }
}

public class Java_090 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.nextSmallest(new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5))).get() == 2,
                s.nextSmallest(new ArrayList<>(Arrays.asList(5, 1, 4, 3, 2))).get() == 2,
                s.nextSmallest(new ArrayList<>(List.of())).isEmpty(),
                s.nextSmallest(new ArrayList<>(Arrays.asList(1, 1))).isEmpty(),
                s.nextSmallest(new ArrayList<>(Arrays.asList(1, 1, 1, 1, 0))).get() == 1,
                s.nextSmallest(new ArrayList<>(Arrays.asList(1, (int) Math.pow(0.0, 0.0)))).isEmpty(),
                s.nextSmallest(new ArrayList<>(Arrays.asList(-35, 34, 12, -45))).get() == -35
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
