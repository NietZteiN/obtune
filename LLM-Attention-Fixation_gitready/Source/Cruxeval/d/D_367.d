import std.math;
import std.typecons;
import std.range;
import std.algorithm;
import std.array;

long[] f(long[] nums, long rmvalue) 
{
    auto res = nums.dup;
    while (res.canFind(rmvalue)) {
        auto index = res.find(rmvalue).front;
        auto popped = res[index];
        if (popped != rmvalue) {
            res ~= popped;
        }
        res = res[0 .. index] ~ res[index + 1 .. $];
    }
    return res;
}
unittest
{
    alias candidate = f;

    assert(candidate([6L, 2L, 1L, 1L, 4L, 1L], 5L) == [6L, 2L, 1L, 1L, 4L, 1L]);
}
void main(){}
