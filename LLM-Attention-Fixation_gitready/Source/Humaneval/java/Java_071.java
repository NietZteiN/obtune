import java.util.*;
import java.lang.*;

class Solution {
    /**
    Given the lengths of the three sides of a triangle. Return the area of
    the triangle rounded to 2 decimal points if the three sides form a valid triangle.
    Otherwise return -1
    Three sides make a valid triangle when the sum of any two sides is greater
    than the third side.
    Example:
    triangleArea(3, 4, 5) == 6.00
    triangleArea(1, 2, 10) == -1
     */
    public double triangleArea(double a, double b, double c) {

        if (a + b <= c || a + c <= b || b + c <= a) {
            return -1;
        }
        double s = (a + b + c) / 2;
        double area = Math.sqrt(s * (s - a) * (s - b) * (s - c));
        area = (double) Math.round(area * 100) / 100;
        return area;
    }
}

public class Java_071 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.triangleArea(3, 4, 5) == 6.00,
                s.triangleArea(1, 2, 10) == -1,
                s.triangleArea(4, 8, 5) == 8.18,
                s.triangleArea(2, 2, 2) == 1.73,
                s.triangleArea(1, 2, 3) == -1,
                s.triangleArea(10, 5, 7) == 16.25,
                s.triangleArea(2, 6, 3) == -1,
                s.triangleArea(1, 1, 1) == 0.43,
                s.triangleArea(2, 2, 10) == -1
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
