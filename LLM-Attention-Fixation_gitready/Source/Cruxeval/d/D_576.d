import std.math;
import std.typecons;
import std.conv;
import std.array;

string[] f(long[] array, long constant) {
    string[] output = ["x"];
    for (size_t i = 1; i <= array.length; ++i) {
        if (i % 2 != 0) {
            output ~= to!string(array[i - 1] * -2);
        } else {
            output ~= to!string(constant);
        }
    }
    return output;
}

unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L], -1L) == ["x", "-2", "-1", "-6"]);
}
void main(){}
