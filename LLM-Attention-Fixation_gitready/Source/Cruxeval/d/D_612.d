import std.math;
import std.typecons;
Nullable!(long[string]) f(Nullable!(long[string]) d) 
{
    return d;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["a": 42L, "b": 1337L, "c": -1L, "d": 5L].nullable);
        assert(!result.isNull && result.get == ["a": 42L, "b": 1337L, "c": -1L, "d": 5L]);
}

}
void main(){}
