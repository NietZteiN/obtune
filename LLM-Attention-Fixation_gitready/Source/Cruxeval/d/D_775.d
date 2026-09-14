import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    long count = nums.length;
    foreach (i; 0 .. count / 2) {
        auto temp = nums[i];
        nums[i] = nums[count - i - 1];
        nums[count - i - 1] = temp;
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([2L, 6L, 1L, 3L, 1L]) == [1L, 3L, 1L, 6L, 2L]);
}
void main(){}
