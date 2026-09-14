import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    long count = nums.length;
    while (nums.length > count/2) {
        nums = [];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([2L, 1L, 2L, 3L, 1L, 6L, 3L, 8L]) == []);
}
void main(){}
