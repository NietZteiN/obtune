import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] array) 
{
    while (array.canFind(-1)) {
        array = array[0 .. $ - 3] ~ array[$ - 2 .. $];
    }
    while (array.canFind(0)) {
        array.popBack();
    }
    while (array.canFind(1)) {
        array = array[1 .. $];
    }
    return array;
}
unittest
{
    alias candidate = f;

    assert(candidate([0L, 2L]) == []);
}
void main(){}
