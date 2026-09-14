import std.math;
import std.typecons;

long[] f(long[] nums) 
{
    long count = 1;
    foreach (i; count .. nums.length - 1)
    {
        nums[i] = nums[i] > nums[count - 1] ? nums[i] : nums[count - 1];
        count += 1;
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L]) == [1L, 2L, 3L]);
}
void main(){}
