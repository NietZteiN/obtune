import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] nums) 
{
    nums.reverse();
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([0L, -5L, -4L]) == [-4L, -5L, 0L]);
}
void main(){}
