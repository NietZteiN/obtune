import std.math;
import std.typecons;

Nullable!(long[string]) f(Nullable!(long[string]) a, Nullable!(long[string]) b) 
{
    if (!a.isNull && !b.isNull) {
        long[string] result = a.get();
        foreach (key, value; b.get()) {
            result[key] = value;
        }
        return Nullable!(long[string])(result);
    }
    return Nullable!(long[string]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["w": 5L, "wi": 10L].nullable, ["w": 3L].nullable);
        assert(!result.isNull && result.get == ["w": 3L, "wi": 10L]);
}

}
void main(){}
