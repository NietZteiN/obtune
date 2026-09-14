import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.conv;
import std.range;
import std.string;

long[] f(string[] a, long[] b) {
    auto d = assocArray(a, b);
    a.sort!((x, y) => d[y] < d[x]);
    return a.map!(x => d[x]).array;
}

unittest
{
    alias candidate = f;

    assert(candidate(["12", "ab"], [2L, 2L]) == [2L, 2L]);
}
void main(){}
