import std.math;
import std.typecons;
import std.algorithm;

Tuple!(string, long)[] f(Nullable!(long[string]) dct) 
{
    Tuple!(string, long)[] lst;
    if (!dct.isNull) {
        auto sortedKeys = dct.get.keys.sort();
        foreach (key; sortedKeys) {
            lst ~= tuple(key, dct.get[key]);
        }
    }
    return lst;
}
unittest
{
    alias candidate = f;

    assert(candidate(["a": 1L, "b": 2L, "c": 3L].nullable) == [tuple("a", 1L), tuple("b", 2L), tuple("c", 3L)]);
}
void main(){}
