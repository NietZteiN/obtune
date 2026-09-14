import java.util.*;
import java.lang.*;

class Solution {
    /**
    You are given a string s.
    Your task is to check if the string is happy or not.
    A string is happy if its length is at least 3 and every 3 consecutive letters are distinct
    For example:
    isHappy(a) => false
    isHappy(aa) => false
    isHappy(abcd) => true
    isHappy(aabb) => false
    isHappy(adb) => true
    isHappy(xyy) => false
     */
    public boolean isHappy(String s) {

        if (s.length() < 3) {
            return false;
        }

        for (int i = 0; i < s.length() - 2; i++) {
            if (s.charAt(i) == s.charAt(i + 1) || s.charAt(i + 1) == s.charAt(i + 2) || s.charAt(i) == s.charAt(i + 2)) {
                return false;
            }
        }
        return true;
    }
}

public class Java_080 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                !s.isHappy("a"),
                !s.isHappy("aa"),
                s.isHappy("abcd"),
                !s.isHappy("aabb"),
                s.isHappy("adb"),
                !s.isHappy("xyy"),
                s.isHappy("iopaxpoi"),
                !s.isHappy("iopaxioi")
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
