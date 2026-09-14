import java.util.*;
import java.lang.*;

class Solution {
    /**
    You're a hungry rabbit, and you already have eaten a certain number of carrots,
    but now you need to eat more carrots to complete the day's meals.
    you should return an array of [ total number of eaten carrots after your meals,
                                    the number of carrots left after your meals ]
    if there are not enough remaining carrots, you will eat all remaining carrots, but will still be hungry.

    Example:
    * eat(5, 6, 10) -> [11, 4]
    * eat(4, 8, 9) -> [12, 1]
    * eat(1, 10, 10) -> [11, 0]
    * eat(2, 11, 5) -> [7, 0]

    Variables:
    @number : integer
        the number of carrots that you have eaten.
    @need : integer
        the number of carrots that you need to eat.
    @remaining : integer
        the number of remaining carrots thet exist in stock

    Constrain:
    * 0 <= number <= 1000
    * 0 <= need <= 1000
    * 0 <= remaining <= 1000

    Have fun :)
     */
    public List<Integer> eat(int number, int need, int remaining) {

        if (need <= remaining) {
            return Arrays.asList(number + need, remaining - need);
        } else {
            return Arrays.asList(number + remaining, 0);
        }
    }
}

public class Java_159 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.eat(5, 6, 10).equals(Arrays.asList(11, 4)),
                s.eat(4, 8, 9).equals(Arrays.asList(12, 1)),
                s.eat(1, 10, 10).equals(Arrays.asList(11, 0)),
                s.eat(2, 11, 5).equals(Arrays.asList(7, 0)),
                s.eat(4, 5, 7).equals(Arrays.asList(9, 2)),
                s.eat(4, 5, 1).equals(Arrays.asList(5, 0))
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
