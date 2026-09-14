import java.util.*;
import java.lang.*;

class Solution {
    /**
    Your task is to implement a function that will simplify the expression
    x * n. The function returns true if x * n evaluates to a whole number and false
    otherwise. Both x and n, are string representation of a fraction, and have the following format,
    <numerator>/<denominator> where both numerator and denominator are positive whole numbers.

    You can assume that x, and n are valid fractions, and do not have zero as denominator.

    simplify("1/5", "5/1") = true
    simplify("1/6", "2/1") = false
    simplify("7/10", "10/2") = false
     */
    public boolean simplify(String x, String n) {

        String[] a = x.split("/");
        String[] b = n.split("/");
        int numerator = Integer.parseInt(a[0]) * Integer.parseInt(b[0]);
        int denom = Integer.parseInt(a[1]) * Integer.parseInt(b[1]);
        return numerator / denom * denom == numerator;
    }
}

public class Java_144 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.simplify("1/5", "5/1") == true,
                s.simplify("1/6", "2/1") == false,
                s.simplify("5/1", "3/1") == true,
                s.simplify("7/10", "10/2") == false,
                s.simplify("2/10", "50/10") == true,
                s.simplify("7/2", "4/2") == true,
                s.simplify("11/6", "6/1") == true,
                s.simplify("2/3", "5/2") == false,
                s.simplify("5/2", "3/5") == false,
                s.simplify("2/4", "8/4") == true,
                s.simplify("2/4", "4/2") == true,
                s.simplify("1/5", "5/1") == true,
                s.simplify("1/5", "1/5") == false
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
