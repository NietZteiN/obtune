import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] array, long[] values) 
{
    array.reverse();
    foreach (value; values)
    {
        array = array[0 .. array.length / 2] ~ [value] ~ array[array.length / 2 .. $];
    }
    array.reverse();
    return array;
}
unittest
{
    alias candidate = f;

    assert(candidate([58L], [21L, 92L]) == [58L, 92L, 21L]);
}
void main(){}
