import std.math;
import std.typecons;
import std.array;

long[] f(long[] nums) 
{
    foreach (i, _; nums)
    {
        nums = nums[0 .. i] ~ [nums[i] * nums[i]] ~ nums[i .. $];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 4L]) == [1L, 1L, 1L, 1L, 2L, 4L]);
}
void main(){}
