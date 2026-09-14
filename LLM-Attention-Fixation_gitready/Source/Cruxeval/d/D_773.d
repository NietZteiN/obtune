import std.math;
import std.typecons;
long f(long[] nums, long n) 
{
    return nums[n];
}
unittest
{
    alias candidate = f;

    assert(candidate([-7L, 3L, 1L, -1L, -1L, 0L, 4L], 6L) == 4L);
}
void main(){}
