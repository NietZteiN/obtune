import std.algorithm;
import std.array;
import std.typecons;

long[] f(long[] nums, long odd1, long odd2) {
    nums = nums.filter!(n => n != odd1 && n != odd2).array;
    return nums;
}

unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L, 7L, 7L, 6L, 8L, 4L, 1L, 2L, 3L, 5L, 1L, 3L, 21L, 1L, 3L], 3L, 1L) == [2L, 7L, 7L, 6L, 8L, 4L, 2L, 5L, 21L]);
}
void main(){}
