import java.util.*;
import java.lang.*;

class Solution {
    /**
    Given a string of words, return a list of words split on whitespace, if no whitespaces exists in the text you
    should split on commas ',' if no commas exists you should return the number of lower-case letters with odd order in the
    alphabet, ord('a') = 0, ord('b') = 1, ... ord('z') = 25
    Examples
    splitWords("Hello world!") == ["Hello", "world!"]
    splitWords("Hello,world!") == ["Hello", "world!"]
    splitWords("abcdef") == 3
     */
    public Object splitWords(String txt) {

        if (txt.contains(" " )) {
            return Arrays.asList(txt.split(" " ));
        } else if (txt.contains("," )) {
            return Arrays.asList(txt.split("[,\s]" ));
        } else {
            int count = 0;
            for (char c : txt.toCharArray()) {
                if (Character.isLowerCase(c) && (c - 'a') % 2 == 1) {
                    count += 1;
                }
            }
            return count;
        }
    }
}

public class Java_125 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                Objects.equals(s.splitWords("Hello world!" ), Arrays.asList("Hello", "world!" )),
                Objects.equals(s.splitWords("Hello,world!" ), Arrays.asList("Hello", "world!" )),
                Objects.equals(s.splitWords("Hello world,!" ), Arrays.asList("Hello", "world,!" )),
                Objects.equals(s.splitWords("Hello,Hello,world !" ), Arrays.asList("Hello,Hello,world", "!" )),
                Objects.equals(s.splitWords("abcdef" ), 3),
                Objects.equals(s.splitWords("aaabb" ), 2),
                Objects.equals(s.splitWords("aaaBb" ), 1),
                Objects.equals(s.splitWords("" ), 0)
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
