import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    long count = nums.length;
    foreach(i; 0 .. count) {
        nums ~= nums[i % 2];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([-1L, 0L, 0L, 1L, 1L]) == [-1L, 0L, 0L, 1L, 1L, -1L, 0L, -1L, 0L, -1L]);
}
void main(){}
