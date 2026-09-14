import std.math;
import std.typecons;

long[] f(long[] nums, long n) 
{
    auto pos = nums.length - 1;
    foreach (i; -nums.length .. 0)
    {
        nums ~= nums[i];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([], 14L) == []);
}
void main(){}
