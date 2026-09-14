import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] nums) 
{
    long m = nums.maxElement();
    foreach (i; 0 .. m) {
        nums = nums.reverse();
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([43L, 0L, 4L, 77L, 5L, 2L, 0L, 9L, 77L]) == [77L, 9L, 0L, 2L, 5L, 77L, 4L, 0L, 43L]);
}
void main(){}
