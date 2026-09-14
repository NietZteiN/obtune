import std.math;
import std.typecons;
long[] f(long[] lst, long i, long n) 
{
    return lst[0 .. i] ~ [n] ~ lst[i .. $];
}
unittest
{
    alias candidate = f;

    assert(candidate([44L, 34L, 23L, 82L, 24L, 11L, 63L, 99L], 4L, 15L) == [44L, 34L, 23L, 82L, 15L, 24L, 11L, 63L, 99L]);
}
void main(){}
