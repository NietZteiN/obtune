import std.math;
import std.typecons;
import std.algorithm;
import std.array;

bool f(long[] nums, long[] mos) 
{
    foreach (num; mos) {
        nums = nums.remove(num);
    }
    nums.sort();
    foreach (num; mos) {
        nums ~= num;
    }
    for (size_t i = 0; i < nums.length - 1; i++) {
        if (nums[i] > nums[i + 1]) {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate([3L, 1L, 2L, 1L, 4L, 1L], [1L]) == false);
}
void main(){}
