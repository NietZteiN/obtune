import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    foreach_reverse(i; 0 .. nums.length) {
        if (nums[i] % 3 == 0) {
            nums ~= nums[i];
        }
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 3L]) == [1L, 3L, 3L]);
}
void main(){}
