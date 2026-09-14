import std.math;
import std.typecons;
long[] f(long[] nums, long i) 
{
    nums = nums[0 .. i] ~ nums[i + 1 .. $];
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([35L, 45L, 3L, 61L, 39L, 27L, 47L], 0L) == [45L, 3L, 61L, 39L, 27L, 47L]);
}
void main(){}
