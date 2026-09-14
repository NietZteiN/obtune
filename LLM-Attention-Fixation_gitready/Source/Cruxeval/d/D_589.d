import std.math;
import std.typecons;
long[] f(long[] num) 
{
    num ~= num[$-1];
    return num;
}
unittest
{
    alias candidate = f;

    assert(candidate([-70L, 20L, 9L, 1L]) == [-70L, 20L, 9L, 1L, 1L]);
}
void main(){}
