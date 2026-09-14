import std.math;
import std.array;
import std.typecons;

Nullable!(long[long]) f(Nullable!(long[long]) dic) 
{
    if (!dic.isNull) {
        long[long] d;
        foreach (key, value; dic.get()) {
            d[key] = value;
        }
        return Nullable!(long[long])(d);
    }
    return Nullable!(long[long]).init;
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
