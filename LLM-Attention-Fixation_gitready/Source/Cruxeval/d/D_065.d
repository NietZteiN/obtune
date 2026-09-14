import std.math;
import std.typecons;
import std.array;

long f(long[] nums, long index) 
{
    auto element = nums[index];
    nums = nums[0 .. index] ~ nums[(index + 1) .. $];
    return element % 42 + element * 2;
}
unittest
{
    alias candidate = f;

    assert(candidate([3L, 2L, 0L, 3L, 7L], 3L) == 9L);
}
void main(){}
