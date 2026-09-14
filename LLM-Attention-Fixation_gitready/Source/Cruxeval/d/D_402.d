import std.math;
import std.typecons;
import std.conv;
import std.algorithm;
import std.array;
import std.string;

Nullable!(long[long]) f(long n, string[] l) {
    long[long] archive;
    for (long i = 0; i < n; ++i) {
        archive.clear();
        foreach (x; l) {
            long key = to!long(x) + 10;
            long value = to!long(x) * 10;
            archive[key] = value;
        }
    }
    return archive.length > 0 ? archive.nullable : Nullable!(long[long]).init;
}

unittest
{
    alias candidate = f;

{
        auto result = candidate(0L, ["aaa", "bbb"]);
        assert(result.isNull);
}

}
void main(){}
