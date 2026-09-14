import std.math;
import std.typecons;
import std.range;
import std.algorithm;
import std.array;

long f(long start, long end, long interval) 
{
    auto steps = iota(start, end +  interval, interval).array;
    if (steps.canFind(1))
        steps[steps.length - 1] = end + 1;
    return steps.length;
}
unittest
{
    alias candidate = f;

    assert(candidate(3L, 10L, 1L) == 8L);
}
void main(){}
