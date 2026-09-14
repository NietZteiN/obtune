import std.math;
import std.typecons;

bool f(long[] nums) 
{
    for(long i = 0; i < nums.length / 2; i++) {
        if (nums[i] != nums[nums.length - i - 1]) {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate([0L, 3L, 6L, 2L]) == false);
}
void main(){}
