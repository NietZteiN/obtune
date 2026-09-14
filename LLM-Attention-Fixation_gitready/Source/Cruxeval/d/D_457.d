import std.math;
import std.typecons;
import std.range;

long[] f(long[] nums) 
{
    auto count = iota(0, nums.length).array;
    foreach (i; 0 .. nums.length)
    {
        nums = nums[1 .. $];
        if (!count.empty)
        {
            count = count[1 .. $];
        }
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([3L, 1L, 7L, 5L, 6L]) == []);
}
void main(){}
