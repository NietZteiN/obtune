import std.math;
import std.typecons;

Nullable!(string[string]) f(Nullable!(string[string]) d) 
{
    if (!d.isNull) {
        d.get().clear();
    }
    return Nullable!(string[string]).init;
}

unittest
{
    alias candidate = f;

{
        auto result = candidate(["a": "3", "b": "-1", "c": "Dum"].nullable);
        assert(result.isNull);
}

}
void main(){}
