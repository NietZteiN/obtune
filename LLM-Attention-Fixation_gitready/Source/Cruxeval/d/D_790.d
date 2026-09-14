import std.math;
import std.typecons;
import std.algorithm;
import std.array;

Tuple!(bool, bool) f(Nullable!(string[string]) d) 
{
    if (!d.isNull) {
        auto r = [d.get().dup, d.get().dup];
        return tuple(r[0] is r[1], r[0] == r[1]);
    }
    return tuple(false, false);
}
unittest
{
    alias candidate = f;

    assert(candidate(["i": "1", "love": "parakeets"].nullable) == tuple(false, true));
}
void main(){}
