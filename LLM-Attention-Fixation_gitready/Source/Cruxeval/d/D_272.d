import std.math;
import std.array;
import std.typecons;

long[] f(long[] base_list, long[] nums) 
{
    base_list ~= nums;
    auto res = base_list.dup;
    foreach_reverse (i; 1..nums.length+1)
    {
        res ~= res[res.length-i];
    }
    return res;
}
unittest
{
    alias candidate = f;

    assert(candidate([9L, 7L, 5L, 3L, 1L], [2L, 4L, 6L, 8L, 0L]) == [9L, 7L, 5L, 3L, 1L, 2L, 4L, 6L, 8L, 0L, 2L, 6L, 0L, 6L, 6L]);
}
void main(){}
