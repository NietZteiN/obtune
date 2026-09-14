import std.math;
import std.typecons;
import std.algorithm;

Nullable!(string[string]) f(Nullable!(string[string]) zoo)
{
    if (!zoo.isNull) {
        auto result = zoo.get();
        foreach (key, value; result) {
            result[value] = key;
            result.remove(key);
        }
        return Nullable!(string[string])(result);
    }
    return Nullable!(string[string]).init;
}

unittest
{
    alias candidate = f;

{
        auto result = candidate(["AAA": "fr"].nullable);
        assert(!result.isNull && result.get == ["fr": "AAA"]);
}

}
void main(){}
