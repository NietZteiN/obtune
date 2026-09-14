import java.util.*;
import java.lang.*;

class Solution {
    /**
    Create a function that returns true if the last character
    of a given string is an alphabetical character and is not
    a part of a word, and false otherwise.
    Note: "word" is a group of characters separated by space.

    Examples:
    checkIfLastCharIsALetter("apple pie") -> false
    checkIfLastCharIsALetter("apple pi e") -> true
    checkIfLastCharIsALetter("apple pi e ") -> false
    checkIfLastCharIsALetter("") -> false
     */
    public boolean checkIfLastCharIsALetter(String txt) {

        String[] words = txt.split(" ", -1);
        String check = words[words.length - 1];
        return check.length() == 1 && Character.isLetter(check.charAt(0));
    }
}

public class Java_134 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.checkIfLastCharIsALetter("apple" ) == false,
                s.checkIfLastCharIsALetter("apple pi e" ) == true,
                s.checkIfLastCharIsALetter("eeeee" ) == false,
                s.checkIfLastCharIsALetter("A" ) == true,
                s.checkIfLastCharIsALetter("Pumpkin pie " ) == false,
                s.checkIfLastCharIsALetter("Pumpkin pie 1" ) == false,
                s.checkIfLastCharIsALetter("" ) == false,
                s.checkIfLastCharIsALetter("eeeee e " ) == false,
                s.checkIfLastCharIsALetter("apple pie" ) == false,
                s.checkIfLastCharIsALetter("apple pi e " ) == false
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
