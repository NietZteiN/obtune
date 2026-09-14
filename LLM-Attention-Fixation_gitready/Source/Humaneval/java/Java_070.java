import java.util.*;
import java.lang.*;

class Solution {
    /**
    Given list of integers, return list in strange order.
    Strange sorting, is when you start with the minimum value,
    then maximum of the remaining integers, then minimum and so on.

    Examples:
    strangeSortList(Arrays.asList(1, 2, 3, 4)) == Arrays.asList(1, 4, 2, 3)
    strangeSortList(Arrays.asList(5, 5, 5, 5)) == Arrays.asList(5, 5, 5, 5)
    strangeSortList(Arrays.asList()) == Arrays.asList()
     */
    public List<Integer> strangeSortList(List<Integer> lst) {

        List<Integer> res = new ArrayList<>();
        boolean _switch = true;
        List<Integer> l = new ArrayList<>(lst);
        while (l.size() != 0) {
            if (_switch) {
                res.add(Collections.min(l));
            } else {
                res.add(Collections.max(l));
            }
            l.remove(res.get(res.size() - 1));
            _switch = !_switch;
        }
        return res;
    }
}

public class Java_070 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.strangeSortList(new ArrayList<>(Arrays.asList(1, 2, 3, 4))).equals(Arrays.asList(1, 4, 2, 3)),
                s.strangeSortList(new ArrayList<>(Arrays.asList(5, 6, 7, 8, 9))).equals(Arrays.asList(5, 9, 6, 8, 7)),
                s.strangeSortList(new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5))).equals(Arrays.asList(1, 5, 2, 4, 3)),
                s.strangeSortList(new ArrayList<>(Arrays.asList(5, 6, 7, 8, 9, 1))).equals(Arrays.asList(1, 9, 5, 8, 6, 7)),
                s.strangeSortList(new ArrayList<>(Arrays.asList(5, 5, 5, 5))).equals(Arrays.asList(5, 5, 5, 5)),
                s.strangeSortList(new ArrayList<>(List.of())).equals(List.of()),
                s.strangeSortList(new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8))).equals(Arrays.asList(1, 8, 2, 7, 3, 6, 4, 5)),
                s.strangeSortList(new ArrayList<>(Arrays.asList(0, 2, 2, 2, 5, 5, -5, -5))).equals(Arrays.asList(-5, 5, -5, 5, 0, 2, 2, 2)),
                s.strangeSortList(new ArrayList<>(List.of(111111))).equals(List.of(111111))
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
