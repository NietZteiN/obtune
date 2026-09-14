import java.util.*;
import java.lang.*;

class Solution {
    /**
    Write a function that takes an integer a and returns true
    if this ingeger is a cube of some integer number.
    Note: you may assume the input is always valid.
    Examples:
    iscube(1) ==> true
    iscube(2) ==> false
    iscube(-1) ==> true
    iscube(64) ==> true
    iscube(0) ==> true
    iscube(180) ==> false
     */
    public boolean iscube(int a) {

        a = Math.abs(a);
        return Math.round(Math.pow(Math.round(Math.pow(a, 1. / 3)), 3)) == a;
    }
}

public class Java_077 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.iscube(1),
                !s.iscube(2),
                s.iscube(-1),
                s.iscube(64),
                !s.iscube(180),
                s.iscube(1000),
                s.iscube(0),
                !s.iscube(1729)
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
