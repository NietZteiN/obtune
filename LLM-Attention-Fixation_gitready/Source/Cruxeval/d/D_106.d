import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] nums) 
{
    long count = nums.length;
    for (long i = 0; i < count; i++)
    {
        nums = nums[0..i] ~ nums[i]*2 ~ nums[i..$];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([2L, 8L, -2L, 9L, 3L, 3L]) == [4L, 4L, 4L, 4L, 4L, 4L, 2L, 8L, -2L, 9L, 3L, 3L]);
}
void main(){}
