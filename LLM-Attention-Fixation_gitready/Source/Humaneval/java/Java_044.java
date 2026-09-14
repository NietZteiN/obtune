import java.util.*;
import java.lang.*;

class Solution {
    /**
    Change numerical base of input number x to base.
    return string representation after the conversion.
    base numbers are less than 10.
    >>> changeBase(8, 3)
    "22"
    >>> changeBase(8, 2)
    "1000"
    >>> changeBase(7, 2)
    "111"
     */
    public String changeBase(int x, int base) {

        StringBuilder ret = new StringBuilder();
        while (x > 0) {
            ret.append(String.valueOf(x % base));
            x /= base;
        }
        return ret.reverse().toString();
    }
}

public class Java_044 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                Objects.equals(s.changeBase(8, 3), "22"),
                Objects.equals(s.changeBase(9, 3), "100"),
                Objects.equals(s.changeBase(234, 2), "11101010"),
                Objects.equals(s.changeBase(16, 2), "10000"),
                Objects.equals(s.changeBase(8, 2), "1000"),
                Objects.equals(s.changeBase(7, 2), "111")
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
        for (int x = 2; x < 8; x++) {
            if (!Objects.equals(s.changeBase(x, x + 1), String.valueOf(x))) {
                throw new AssertionError();
            }
        }
    }
}
