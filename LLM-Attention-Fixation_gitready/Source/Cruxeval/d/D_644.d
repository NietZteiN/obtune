import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] nums, long pos) 
{
    auto s = pos % 2 != 0 ? nums.length - 1 : nums.length;
    nums[0 .. s].reverse();
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([6L, 1L], 3L) == [6L, 1L]);
}
void main(){}
