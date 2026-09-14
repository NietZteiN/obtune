import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] nums, long start, long k) 
{
    nums[start .. start + k] = nums[start .. start + k].array.reverse();
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L, 4L, 5L, 6L], 4L, 2L) == [1L, 2L, 3L, 4L, 6L, 5L]);
}
void main(){}
