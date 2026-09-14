import java.util.*;
import java.lang.*;

class Solution {
    /**
    Check if two words have the same characters.
    >>> sameChars("eabcdzzzz", "dddzzzzzzzddeddabc")
    true
    >>> sameChars("abcd", "dddddddabc")
    true
    >>> sameChars("dddddddabc", "abcd")
    true
    >>> sameChars("eabcd", "dddddddabc")
    false
    >>> sameChars("abcd", "dddddddabce")
    false
    >>> sameChars("eabcdzzzz", "dddzzzzzzzddddabc")
    false
     */
    public boolean sameChars(String s0, String s1) {

        Set<Character> set0 = new HashSet<>();
        for (char c : s0.toCharArray()) {
            set0.add(c);
        }
        Set<Character> set1 = new HashSet<>();
        for (char c : s1.toCharArray()) {
            set1.add(c);
        }
        return set0.equals(set1);
    }
}

public class Java_054 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.sameChars("eabcdzzzz", "dddzzzzzzzddeddabc"),
                s.sameChars("abcd", "dddddddabc"),
                s.sameChars("dddddddabc", "abcd"),
                !s.sameChars("eabcd", "dddddddabc"),
                !s.sameChars("abcd", "dddddddabcf"),
                !s.sameChars("eabcdzzzz", "dddzzzzzzzddddabc"),
                !s.sameChars("aabb", "aaccc")
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
