import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] nums, long sort_count) 
{
    sort(nums);
    return nums[0 .. sort_count];
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 2L, 3L, 4L, 5L], 1L) == [1L]);
}
void main(){}
