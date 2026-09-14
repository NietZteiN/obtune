import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    foreach(i; 0 .. nums.length) {
        if (i % 2 == 0) {
            nums ~= nums[i] * nums[i + 1];
        }
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == []);
}
void main(){}
