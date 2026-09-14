import std.math;
import std.typecons;
import std.conv;

long[] f(long[] a) 
{
    long[] b = a.dup;
    for (long k = 0; k < a.length - 1; k += 2)
    {
        b = b[0 .. k] ~ b[k] ~ b[k .. $];
    }
    b ~= b[0];
    return b;
}
unittest
{
    alias candidate = f;

    assert(candidate([5L, 5L, 5L, 6L, 4L, 9L]) == [5L, 5L, 5L, 5L, 5L, 5L, 6L, 4L, 9L, 5L]);
}
void main(){}
