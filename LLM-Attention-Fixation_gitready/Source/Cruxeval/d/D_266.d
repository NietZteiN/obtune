import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    foreach_reverse(i; 0 .. nums.length) {
        if (nums[i] % 2 == 1) {
            nums = nums[0 .. i+1] ~ [nums[i]] ~ nums[i+1 .. $];
        }
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([2L, 3L, 4L, 6L, -2L]) == [2L, 3L, 3L, 4L, 6L, -2L]);
}
void main(){}
