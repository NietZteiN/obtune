import java.util.*;
import java.lang.*;

class Solution {
    /**
    In this problem, you will implement a function that takes two lists of numbers,
    and determines whether it is possible to perform an exchange of elements
    between them to make lst1 a list of only even numbers.
    There is no limit on the number of exchanged elements between lst1 and lst2.
    If it is possible to exchange elements between the lst1 and lst2 to make
    all the elements of lst1 to be even, return "YES".
    Otherwise, return "NO".
    For example:
    exchange(Arrays.asList(1, 2, 3, 4), Arrays.asList(1, 2, 3, 4)) => "YES"
    exchange(Arrays.asList(1, 2, 3, 4), Arrays.asList(1, 5, 3, 4)) => "NO"
    It is assumed that the input lists will be non-empty.
     */
    public String exchange(List<Integer> lst1, List<Integer> lst2) {

        int odd = 0, even = 0;
        for (int i : lst1) {
            if (i % 2 == 1) {
                odd += 1;
            }
        }
        for (int i : lst2) {
            if (i % 2 == 0) {
                even += 1;
            }
        }
        if (even >= odd) {
            return "YES";
        }
        return "NO";
    }
}

public class Java_110 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                Objects.equals(s.exchange(Arrays.asList(1, 2, 3, 4), Arrays.asList(1, 2, 3, 4)), "YES" ),
                Objects.equals(s.exchange(Arrays.asList(1, 2, 3, 4), Arrays.asList(1, 5, 3, 4)), "NO" ),
                Objects.equals(s.exchange(Arrays.asList(1, 2, 3, 4), Arrays.asList(2, 1, 4, 3)), "YES" ),
                Objects.equals(s.exchange(Arrays.asList(5, 7, 3), Arrays.asList(2, 6, 4)), "YES" ),
                Objects.equals(s.exchange(Arrays.asList(5, 7, 3), Arrays.asList(2, 6, 3)), "NO" ),
                Objects.equals(s.exchange(Arrays.asList(3, 2, 6, 1, 8, 9), Arrays.asList(3, 5, 5, 1, 1, 1)), "NO" ),
                Objects.equals(s.exchange(Arrays.asList(100, 200), Arrays.asList(200, 200)), "YES" )
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
