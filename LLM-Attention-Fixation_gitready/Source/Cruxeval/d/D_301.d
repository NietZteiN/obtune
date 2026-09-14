import std.math;
import std.typecons;

long[] f(long[] nums) 
{
    for (long i = -nums.length + 1; i < 0; i++)
    {
        nums ~= [nums[nums.length + i], nums[nums.length + i]];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([0L, 6L, 2L, -1L, -2L]) == [0L, 6L, 2L, -1L, -2L, 6L, 6L, -2L, -2L, -2L, -2L, -2L, -2L]);
}
void main(){}
