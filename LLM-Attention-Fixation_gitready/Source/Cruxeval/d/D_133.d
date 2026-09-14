import std.math;
import std.typecons;
long[] f(long[] nums, long[] elements) 
{
    long[] result;
    foreach (i; 0 .. elements.length) {
        result ~= nums[$-1];
        nums = nums[0 .. $-1];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([7L, 1L, 2L, 6L, 0L, 2L], [9L, 0L, 3L]) == [7L, 1L, 2L]);
}
void main(){}
