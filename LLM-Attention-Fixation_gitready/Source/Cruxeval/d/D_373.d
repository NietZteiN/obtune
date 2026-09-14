import std.math;
import std.typecons;
import std.array;

long[] f(long[] orig) 
{
    auto copy = orig.dup;
    copy ~= 100;
    copy = array(copy[0 .. $-1]);
    return copy;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L]) == [1L, 2L, 3L]);
}
void main(){}
