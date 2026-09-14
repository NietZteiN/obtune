import std.algorithm;
import std.array;
import std.math;
import std.typecons;

long[] f(long[] nums) {
    nums = nums.filter!(y => y > 0).array;
    if (nums.length <= 3) {
        return nums;
    }
    nums.reverse();
    size_t half = nums.length / 2;
    return nums[0 .. half].array ~ [0L, 0L, 0L, 0L, 0L] ~ nums[half .. $].array;
}

unittest
{
    alias candidate = f;

    assert(candidate([10L, 3L, 2L, 2L, 6L, 0L]) == [6L, 2L, 0L, 0L, 0L, 0L, 0L, 2L, 3L, 10L]);
}
void main(){}
