import std.math;
import std.typecons;

Nullable!(long[string]) f(Nullable!(long[string]) obj) 
{
    if (!obj.isNull) {
        auto map = obj.get();
        foreach (k, v; map) {
            if (v >= 0) {
                map[k] = -v;
            }
        }
        return Nullable!(long[string])(map);
    }
    return Nullable!(long[string]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["R": 0L, "T": 3L, "F": -6L, "K": 0L].nullable);
        assert(!result.isNull && result.get == ["R": 0L, "T": -3L, "F": -6L, "K": 0L]);
}

}
void main(){}
