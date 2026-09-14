import java.util.*;
import java.lang.*;

class Solution {
    /**
    Write a function that accepts a list of strings.
    The list contains different words. Return the word with maximum number
    of unique characters. If multiple strings have maximum number of unique
    characters, return the one which comes first in lexicographical order.

    findMax(["name", "of", "string"]) == "string"
    findMax(["name", "enam", "game"]) == "enam"
    findMax(["aaaaaaa", "bb" ,"cc"]) == ""aaaaaaa"
     */
    public String findMax(List<String> words) {

        List<String> words_sort = new ArrayList<>(words);
        words_sort.sort(new Comparator<String>() {
            @Override
            public int compare(String o1, String o2) {
                Set<Character> s1 = new HashSet<>();
                for (char ch : o1.toCharArray()) {
                    s1.add(ch);
                }
                Set<Character> s2 = new HashSet<>();
                for (char ch : o2.toCharArray()) {
                    s2.add(ch);
                }
                if (s1.size() > s2.size()) {
                    return 1;
                } else if (s1.size() < s2.size()) {
                    return -1;
                } else {
                    return -o1.compareTo(o2);
                }
            }
        });
        return words_sort.get(words_sort.size() - 1);
    }
}

public class Java_158 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.findMax(new ArrayList<>(Arrays.asList("name", "of", "string"))).equals("string"),
                s.findMax(new ArrayList<>(Arrays.asList("name", "enam", "game"))).equals("enam"),
                s.findMax(new ArrayList<>(Arrays.asList("aaaaaaa", "bb", "cc"))).equals("aaaaaaa"),
                s.findMax(new ArrayList<>(Arrays.asList("abc", "cba"))).equals("abc"),
                s.findMax(new ArrayList<>(Arrays.asList("play", "this", "game", "of", "footbott"))).equals("footbott"),
                s.findMax(new ArrayList<>(Arrays.asList("we", "are", "gonna", "rock"))).equals("gonna"),
                s.findMax(new ArrayList<>(Arrays.asList("we", "are", "a", "mad", "nation"))).equals("nation"),
                s.findMax(new ArrayList<>(Arrays.asList("this", "is", "a", "prrk"))).equals("this"),
                s.findMax(new ArrayList<>(List.of("b"))).equals("b"),
                s.findMax(new ArrayList<>(Arrays.asList("play", "play", "play"))).equals("play")
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
