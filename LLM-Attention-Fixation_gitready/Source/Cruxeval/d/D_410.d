import std.math;
import std.typecons;
import std.range;
import std.array;

long[] f(long[] nums)
{
    long a = 0;
    foreach (i; 0 .. nums.length)
    {
        nums = nums[0 .. i] ~ nums[a] ~ nums[i .. nums.length];
        a += 1;
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 3L, -1L, 1L, -2L, 6L]) == [1L, 1L, 1L, 1L, 1L, 1L, 1L, 3L, -1L, 1L, -2L, 6L]);
}
void main(){}
