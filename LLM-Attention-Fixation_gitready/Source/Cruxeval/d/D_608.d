import std.math;
import std.typecons;

Nullable!(long[long]) f(Nullable!(long[long]) aDict) 
{
    if (!aDict.isNull) {
        long[long] result;
        foreach (k, v; aDict.get()) {
            result[v] = k;
        }
        return Nullable!(long[long])(result);
    }
    return Nullable!(long[long]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate([1L: 1L, 2L: 2L, 3L: 3L].nullable);
        assert(!result.isNull && result.get == [1L: 1L, 2L: 2L, 3L: 3L]);
}

}
void main(){}
