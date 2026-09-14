import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    auto count = nums.length / 2;
    foreach (_; 0 .. count) {
        nums = nums[1 .. $];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([3L, 4L, 1L, 2L, 3L]) == [1L, 2L, 3L]);
}
void main(){}
