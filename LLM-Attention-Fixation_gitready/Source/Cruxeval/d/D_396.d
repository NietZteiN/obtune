import std.math;
import std.typecons;

Nullable!(long[long]) f(Nullable!(long[long]) ets) 
{
    if (!ets.isNull) {
        foreach (k, v; ets.get()) {
            ets.get()[k] = v * v;
        }
    }
    return ets;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(Nullable!(long[long]).init);
        assert(result.isNull);
}

}
void main(){}
