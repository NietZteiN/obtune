import std.math;
import std.typecons;
long[] f(long[] xs) 
{
    foreach_reverse (idx; 0 .. xs.length)
    {
        xs = xs[$-1 .. $] ~ xs[0 .. $-1];
    }
    return xs;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L]) == [1L, 2L, 3L]);
}
void main(){}
