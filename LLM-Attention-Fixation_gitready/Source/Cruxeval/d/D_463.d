import std.math;
import std.typecons;

Nullable!(long[long]) f(Nullable!(long[long]) dict) 
{
    if (!dict.isNull) {
        long[long] result = dict.get();
        foreach (k, v; result) {
            if (v in result) {
                result.remove(k);
            }
        }
        return Nullable!(long[long])(result);
    }
    return Nullable!(long[long]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate([-1L: -1L, 5L: 5L, 3L: 6L, -4L: -4L].nullable);
        assert(!result.isNull && result.get == [3L: 6L]);
}

}
void main(){}
