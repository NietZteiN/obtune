import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] nums) 
{
    auto count = nums.length;
    foreach (num; 2 .. count) {
        nums.sort();
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([-6L, -5L, -7L, -8L, 2L]) == [-8L, -7L, -6L, -5L, 2L]);
}
void main(){}
