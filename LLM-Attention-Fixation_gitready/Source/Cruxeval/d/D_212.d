import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] nums) 
{
    foreach(_; 0 .. nums.length - 1) {
        nums = nums.reverse;
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, -9L, 7L, 2L, 6L, -3L, 3L]) == [1L, -9L, 7L, 2L, 6L, -3L, 3L]);
}
void main(){}
