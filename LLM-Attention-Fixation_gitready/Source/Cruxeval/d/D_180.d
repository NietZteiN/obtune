import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] nums) 
{
    long a = -1;
    long[] b = nums[1..$];
    while (a <= b[0]) {
        nums = nums.filter!(x => x != b[0]).array;
        a = 0;
        b = b[1..$];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([-1L, 5L, 3L, -2L, -6L, 8L, 8L]) == [-1L, -2L, -6L, 8L, 8L]);
}
void main(){}
