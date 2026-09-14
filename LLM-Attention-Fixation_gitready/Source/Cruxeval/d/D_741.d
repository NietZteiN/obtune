import std.math;
import std.typecons;
long f(long[] nums, long p) 
{
    long prev_p = p - 1;
    if (prev_p < 0) {
        prev_p = nums.length - 1;
    }
    return nums[prev_p];
}
unittest
{
    alias candidate = f;

    assert(candidate([6L, 8L, 2L, 5L, 3L, 1L, 9L, 7L], 6L) == 1L);
}
void main(){}
