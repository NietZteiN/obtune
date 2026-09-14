import std.math;
import std.typecons;
long[] f(long[] nums, long idx, long added) 
{
    nums = nums[0 .. idx] ~ [added] ~ nums[idx .. $];
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([2L, 2L, 2L, 3L, 3L], 2L, 3L) == [2L, 2L, 3L, 2L, 3L, 3L]);
}
void main(){}
