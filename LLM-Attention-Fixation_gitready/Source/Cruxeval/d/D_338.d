import std.math;
import std.typecons;

Nullable!(string[long]) f(Nullable!(long[string]) my_dict)
{
    if (!my_dict.isNull) {
        string[long] result;
        foreach (k, v; my_dict.get()) {
            result[v] = k;
        }
        return Nullable!(string[long])(result);
    }
    return Nullable!(string[long]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["a": 1L, "b": 2L, "c": 3L, "d": 2L].nullable);
        assert(!result.isNull && result.get == [1L: "a", 2L: "d", 3L: "c"]);
}

}
void main(){}
