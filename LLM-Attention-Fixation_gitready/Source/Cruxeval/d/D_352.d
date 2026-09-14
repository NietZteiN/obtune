import std.math;
import std.typecons;
long f(long[] nums) 
{
    return nums[nums.length / 2];
}
unittest
{
    alias candidate = f;

    assert(candidate([-1L, -3L, -5L, -7L, 0L]) == -5L);
}
void main(){}
