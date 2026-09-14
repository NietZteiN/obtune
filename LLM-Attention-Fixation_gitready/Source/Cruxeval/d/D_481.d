import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] values, long item1, long item2) 
{
    if (values.back == item2) {
        if (count(values[1..$], values[0]) == 0) {
            values ~= values[0];
        }
    } else if (values.back == item1) {
        if (values[0] == item2) {
            values ~= values[0];
        }
    }
    return values;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 1L], 2L, 3L) == [1L, 1L]);
}
void main(){}
