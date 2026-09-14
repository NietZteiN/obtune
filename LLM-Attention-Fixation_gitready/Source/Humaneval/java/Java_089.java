import java.util.*;
import java.lang.*;

class Solution {
    /**
    Create a function encrypt that takes a string as an argument and
    returns a string encrypted with the alphabet being rotated.
    The alphabet should be rotated in a manner such that the letters
    shift down by two multiplied to two places.
    For example:
    encrypt("hi") returns "lm"
    encrypt("asdfghjkl") returns "ewhjklnop"
    encrypt("gf") returns "kj"
    encrypt("et") returns "ix"
     */
    public String encrypt(String s) {

        StringBuilder sb = new StringBuilder();
        for (char c : s.toCharArray()) {
            if (Character.isLetter(c)) {
                sb.append((char) ('a' + (c - 'a' + 2 * 2) % 26));
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }
}

public class Java_089 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                Objects.equals(s.encrypt("hi"), "lm"),
                Objects.equals(s.encrypt("asdfghjkl"), "ewhjklnop"),
                Objects.equals(s.encrypt("gf"), "kj"),
                Objects.equals(s.encrypt("et"), "ix"),
                Objects.equals(s.encrypt("faewfawefaewg"), "jeiajeaijeiak"),
                Objects.equals(s.encrypt("hellomyfriend"), "lippsqcjvmirh"),
                Objects.equals(s.encrypt("dxzdlmnilfuhmilufhlihufnmlimnufhlimnufhfucufh"), "hbdhpqrmpjylqmpyjlpmlyjrqpmqryjlpmqryjljygyjl"),
                Objects.equals(s.encrypt("a"), "e")
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
