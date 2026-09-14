import std.math;
import std.typecons;

long[] f(long[] nums, long pop1, long pop2) 
{
    if (pop1 > 0 && pop1 <= nums.length)
    {
        nums = nums[0 .. pop1-1] ~ nums[pop1 .. $];
    }
    if (pop2 > 0 && pop2 <= nums.length)
    {
        nums = nums[0 .. pop2-1] ~ nums[pop2 .. $];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 5L, 2L, 3L, 6L], 2L, 4L) == [1L, 2L, 3L]);
}
void main(){}
