import java.util.*;
import java.lang.*;

class Solution {
    /**
    returns encoded string by cycling groups of three characters.
     */
    public String encodeCyclic(String s) {
        // split string to groups. Each of length 3.
        List<String> groups = new ArrayList<>();
        for (int i = 0; i < s.length(); i += 3) {
            groups.add(s.substring(i, Math.min(i + 3, s.length())));
        }
        // cycle elements in each group. Unless group has fewer elements than 3.
        for (int i = 0; i < groups.size(); i++) {
            if (groups.get(i).length() == 3) {
                groups.set(i, groups.get(i).substring(1) + groups.get(i).charAt(0));
            }
        }
        return String.join("", groups);
    }

    /**
    takes as input string encoded with encodeCyclic function. Returns decoded string.
     */
    public String decodeCyclic(String s) {

        return encodeCyclic(encodeCyclic(s));
    }
}

public class Java_038 {
    static char[] letters = "abcdefghijklmnopqrstuvwxyz".toCharArray();
    static Random rand = new Random(42);
    public static String random_string(int length) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < length; i++) {
            sb.append(letters[rand.nextInt(26)]);
        }
        return sb.toString();
    }
    public static void main(String[] args) {
        Solution s = new Solution();
        for (int i = 0; i < 100; i++) {
            String str = random_string(rand.nextInt(10) + 10);
            String encode_str = s.encodeCyclic(str);
            if (!s.decodeCyclic(encode_str).equals(str)) {
                throw new AssertionError();
            }
        }
    }
}
