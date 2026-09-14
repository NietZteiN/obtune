import std.math;
import std.typecons;
import std.algorithm : remove;

Nullable!(long[string]) f(Nullable!(long[string]) d)
{
    if (!d.isNull)
    {
        auto copyD = d.get();
        if (copyD.length > 0)
        {
            copyD.remove(copyD.keys[0]);
        }
        return Nullable!(long[string])(copyD);
    }
    return Nullable!(long[string]).init;
}

unittest
{
    alias candidate = f;

{
        auto result = candidate(["l": 1L, "t": 2L, "x:": 3L].nullable);
        assert(!result.isNull && result.get == ["l": 1L, "t": 2L]);
}

}
void main(){}
