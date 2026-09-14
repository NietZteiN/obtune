import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.conv;
import std.string;
import std.range;

long[] f(Tuple!(string, long)[] parts) {
    auto dict = parts.assocArray;
    long[] result;
    foreach (part; parts) {
        if (part[0] in dict) {
            result ~= dict[part[0]];
            dict.remove(part[0]);
        }
    }
    return result;
}

unittest
{
    alias candidate = f;

    assert(candidate([tuple("u", 1L), tuple("s", 7L), tuple("u", -5L)]) == [-5L, 7L]);
}
void main(){}
