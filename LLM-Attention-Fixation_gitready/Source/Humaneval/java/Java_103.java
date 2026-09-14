import java.util.*;
import java.lang.*;

class Solution {
    /**
    You are given two positive integers n and m, and your task is to compute the
    average of the integers from n through m (including n and m).
    Round the answer to the nearest integer and convert that to binary.
    If n is greater than m, return -1.
    Example:
    roundedAvg(1, 5) => "11"
    roundedAvg(7, 5) => -1
    roundedAvg(10, 20) => "1111"
    roundedAvg(20, 33) => "11011"
     */
    public Object roundedAvg(int n, int m) {

        if (n > m) {
            return -1;
        }
        return Integer.toBinaryString((int) Math.round((double) (m + n) / 2));
    }
}

public class Java_103 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                Objects.equals((String) s.roundedAvg(1, 5), "11" ),
                Objects.equals((String) s.roundedAvg(7, 13), "1010" ),
                Objects.equals((String) s.roundedAvg(964, 977), "1111001011" ),
                Objects.equals((String) s.roundedAvg(996, 997), "1111100101" ),
                Objects.equals((String) s.roundedAvg(560, 851), "1011000010" ),
                Objects.equals((String) s.roundedAvg(185, 546), "101101110" ),
                Objects.equals((String) s.roundedAvg(362, 496), "110101101" ),
                Objects.equals((String) s.roundedAvg(350, 902), "1001110010" ),
                Objects.equals((String) s.roundedAvg(197, 233), "11010111" ),
                (int) s.roundedAvg(7, 5) == -1,
                (int) s.roundedAvg(5, 1) == -1,
                Objects.equals((String) s.roundedAvg(5, 5), "101" )
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
