import java.util.*;
import java.lang.*;

class Solution {
    /**
    Given the lengths of the three sides of a triangle. Return true if the three
    sides form a right-angled triangle, false otherwise.
    A right-angled triangle is a triangle in which one angle is right angle or
    90 degree.
    Example:
    rightAngleTriangle(3, 4, 5) == true
    rightAngleTriangle(1, 2, 3) == false
     */
    public boolean rightAngleTriangle(int a, int b, int c) {

        return a * a == b * b + c * c || b * b == a * a + c * c || c * c == a * a + b * b;
    }
}

public class Java_157 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.rightAngleTriangle(3, 4, 5) == true,
                s.rightAngleTriangle(1, 2, 3) == false,
                s.rightAngleTriangle(10, 6, 8) == true,
                s.rightAngleTriangle(2, 2, 2) == false,
                s.rightAngleTriangle(7, 24, 25) == true,
                s.rightAngleTriangle(10, 5, 7) == false,
                s.rightAngleTriangle(5, 12, 13) == true,
                s.rightAngleTriangle(15, 8, 17) == true,
                s.rightAngleTriangle(48, 55, 73) == true,
                s.rightAngleTriangle(1, 1, 1) == false,
                s.rightAngleTriangle(2, 2, 10) == false
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
