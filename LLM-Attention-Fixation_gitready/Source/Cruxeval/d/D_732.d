import std.math;
import std.typecons;

Nullable!(long[string]) f(Nullable!(long[string]) char_freq) 
{
    if (!char_freq.isNull) {
        long[string] result;
        foreach (key, value; char_freq.get()) {
            result[key] = value / 2;
        }
        return Nullable!(long[string])(result);
    }
    return Nullable!(long[string]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["u": 20L, "v": 5L, "b": 7L, "w": 3L, "x": 3L].nullable);
        assert(!result.isNull && result.get == ["u": 10L, "v": 2L, "b": 3L, "w": 1L, "x": 1L]);
}

}
void main(){}
