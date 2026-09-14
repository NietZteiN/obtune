import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] array) 
{
    auto l = array.length;
    if (l % 2 == 0) {
        array.length = 0;
    } else {
        array.reverse();
    }
    return array;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == []);
}
void main(){}
