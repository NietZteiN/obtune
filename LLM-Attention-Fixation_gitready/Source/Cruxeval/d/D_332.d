import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    auto count = nums.length;
    if (count == 0) {
        nums = new long[](cast(size_t)nums[$-1]);
    } else if (count % 2 == 0) {
        nums = [];
    } else {
        nums = nums[count/2..$];
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([-6L, -2L, 1L, -3L, 0L, 1L]) == []);
}
void main(){}
