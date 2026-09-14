import std.algorithm;
import std.array;
import std.stdio;
import std.range;

long[] f(string[] names, string[] winners) {
    auto indices = names.enumerate.filter!(x => winners.canFind(x.value)).map!(x => cast(long)x.index).array;
    indices.sort!((a, b) => b < a);
    return indices;
}

unittest
{
    alias candidate = f;

    assert(candidate(["e", "f", "j", "x", "r", "k"], ["a", "v", "2", "im", "nb", "vj", "z"]) == []);
}
void main(){}
